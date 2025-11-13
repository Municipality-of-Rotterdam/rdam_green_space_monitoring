"""Parallel entry script for pc_prep."""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pc_prep.logger import logger
from pc_prep.tree_prep.prep_pc import process_single_pc

_G_ARGS = None


def _parse_args_from_program_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--reference_trees_path", type=str, required=True)
    parser.add_argument("--pc_raw_metadata", type=str, required=True)
    parser.add_argument("--bgt_pavements_raw", type=str, required=True)

    # NEW: current step's mount root for pc_raw
    parser.add_argument("--pc_raw", type=str, required=True)

    parser.add_argument("--img_dir", type=str, required=True)
    parser.add_argument("--pc_dir", type=str, required=True)
    parser.add_argument("--bgt_dir", type=str, required=True)

    parser.add_argument("--resolution", type=float, default=0.05)
    parser.add_argument("--num_workers", type=int, default=1)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")

    # placeholders for prepare_output_paths
    parser.add_argument("--img_metadata", default="__unused_img_metadata.json")
    parser.add_argument("--pc_metadata", default="__unused_pc_metadata.json")
    parser.add_argument("--bgt_metadata", default="__unused_bgt_metadata.json")
    args, _ = parser.parse_known_args()
    return args


def init() -> None:
    """Init script."""
    global _G_ARGS  # noqa: PLW0603
    _G_ARGS = _parse_args_from_program_arguments()
    for d in (_G_ARGS.img_dir, _G_ARGS.pc_dir, _G_ARGS.bgt_dir):
        os.makedirs(d, exist_ok=True)
    logger.info("Init complete. pc_raw mount: %s", _G_ARGS.pc_raw)


def _row_to_abs_path(row: str) -> str | None:
    # If string points to a JSON file, read {"rel_path": "..."}
    if isinstance(row, str):
        p = Path(row)
        if p.suffix.lower() == ".json" and p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                rel = data.get("rel_path")
                if rel:
                    return str(Path(_G_ARGS.pc_raw) / rel)  # type: ignore[union-attr]
            except Exception as ex:
                logger.exception("Failed to read item file %s: %s", p, ex)
                return None
    return None


def _process_paths(paths: List[str]) -> Tuple[List[Dict[str, Any]], int]:
    rows: List[Dict[str, Any]] = []
    ok = 0
    for pc_path in paths:
        if not pc_path:
            continue
        pc_path_norm = os.path.normpath(pc_path)

        res = process_single_pc(pc_path=pc_path_norm, args=_G_ARGS)
        if res:
            rows.append(res)
            ok += 1
    return rows, ok


def run(mini_batch: List[Any]) -> List[Dict[str, Any]]:
    """Run script.
    Translate each row to an absolute path under this step's mount.
    """
    abs_paths = [p for p in (_row_to_abs_path(r) for r in mini_batch) if p]
    logger.info("Mini-batch: %d items", len(abs_paths))
    rows, ok = _process_paths(abs_paths)
    logger.info("Succeeded on %d/%d", ok, len(abs_paths))
    return rows


def shutdown() -> None:
    """Shutdown script."""
    logger.info("Shutdown.")
