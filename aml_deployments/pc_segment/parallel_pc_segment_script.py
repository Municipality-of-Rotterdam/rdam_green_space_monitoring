"""Script for parallel processing of pc_segment."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pc_segment.logger import logger
from pc_segment.segment_pc import initialize_model, segment_batch_items

_G: Dict[str, Any] = {"args": None, "predictor": None}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--model_mount", type=str, required=True)
    p.add_argument("--img_dir_mount", type=str, required=True)
    p.add_argument("--segment_dir", type=str, required=True)
    p.add_argument("--batch_size", type=int, default=2)
    p.add_argument("--debug", action="store_true")
    args, _ = p.parse_known_args()
    return args


def init() -> None:
    """Init script."""
    _G["args"] = _parse_args()
    Path(_G["args"].segment_dir).mkdir(parents=True, exist_ok=True)
    _G["predictor"] = initialize_model(model_path=_G["args"].model_mount)
    logger.info(
        "init(): model=%s | img_dir=%s | segment_dir=%s | batch_size=%s",
        _G["args"].model_mount,
        _G["args"].img_dir_mount,
        _G["args"].segment_dir,
        _G["args"].batch_size,
    )


def _read_items(mini_batch: List[Any]) -> Tuple[List[str], List[Dict[str, str]]]:
    """Function to read items.

    Each item is usually a JSON file path created by the planner.
      {"key":"<pc_path-like key>", "img_rel":"<rel to img_dir>", "prompt_rel":"<optional rel>"}
    Returns (keys, preprocessing_list) where each prep dict matches what your code expects:
      {"img_path": "...", "prompt_path": "...?"}
    """
    keys: List[str] = []
    preps: List[Dict[str, str]] = []
    for it in mini_batch:
        if isinstance(it, dict):
            data = it
        else:
            p = Path(str(it))
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as ex:
                logger.warning("Unreadable item %s: %s", it, ex)
                continue

        key = data.get("key")
        img_rel = data.get("img_rel")
        prompt_rel = data.get("prompt_rel")
        if not key or not img_rel:
            logger.warning("Skipping item missing key/img_rel: %s", data)
            continue

        prep = {"img_path": img_rel}
        if prompt_rel:
            prep["prompt_path"] = prompt_rel
        keys.append(key)
        preps.append(prep)
    return keys, preps


def run(mini_batch: List[Any]) -> List[str]:
    """Run script."""
    # Build inputs for batched function
    keys, preps = _read_items(mini_batch)
    if not keys:
        # Always return at least one line so AML marks the mini-batch as non-empty
        return [json.dumps({"skip": {"reason": "empty mini-batch"}})]

    mapping = segment_batch_items(
        keys=keys,
        preprocessing_list=preps,
        img_dir=_G["args"].img_dir_mount,
        segment_dir=_G["args"].segment_dir,
        predictor=_G["predictor"],
        debug=_G["args"].debug,
        batch_size=_G["args"].batch_size,
    )

    # Emit one JSON line per *input key* (success or skip if not produced)
    lines: List[str] = []
    for k in keys:
        if k in mapping:
            lines.append(json.dumps({k: mapping[k]}))
        else:
            lines.append(json.dumps({"skip": {"key": k}}))
    return lines  # JSON strings → proper JSONL


def shutdown() -> None:
    """Shutdown script."""
    logger.info("shutdown()")
