"""Script for parallel processing of tree_modeling."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

from tree_modeling.logger import logger
from tree_modeling.modeling_tree import process_point_cloud

_G: Dict[str, Any] = {"args": None, "ops_metadata": None, "bgt_metadata": None}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--ops_dir_mount", type=str, required=True)
    p.add_argument("--ops_metadata", type=str, required=True)
    p.add_argument("--bgt_dir_mount", type=str, required=True)
    p.add_argument("--bgt_metadata", type=str, required=True)
    p.add_argument("--modeling_dir", type=str, required=True)
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--debug", action="store_true")
    args, _ = p.parse_known_args()
    return args


def init() -> None:
    """Init script."""
    _G["args"] = _parse_args()
    _G["ops_metadata"] = json.loads(
        Path(_G["args"].ops_metadata).read_text(encoding="utf-8")
    )
    _G["bgt_metadata"] = json.loads(
        Path(_G["args"].bgt_metadata).read_text(encoding="utf-8")
    )
    Path(_G["args"].modeling_dir).mkdir(parents=True, exist_ok=True)
    logger.info("init(): modeling_dir=%s", _G["args"].modeling_dir)


def _read_item(it: str) -> str | None:
    p = Path(str(it))
    if p.suffix.lower() == ".json" and p.exists():
        try:
            val = json.loads(p.read_text(encoding="utf-8")).get("pc_path")
            return val if isinstance(val, str) else None
        except Exception:
            return None
    return None


def _make_cli_args(base: argparse.Namespace) -> SimpleNamespace:
    """Build the args namespace that process_point_cloud expects."""
    return SimpleNamespace(
        ops_dir=base.ops_dir_mount,
        bgt_dir=base.bgt_dir_mount,
        modeling_dir=base.modeling_dir,
        overwrite=base.overwrite,
        debug=base.debug,
    )


def run(mini_batch: List[Any]) -> List[str]:
    """Run script."""
    lines: List[str] = []
    cli_args = _make_cli_args(_G["args"])
    for it in mini_batch:
        pc_path = _read_item(it)
        if not pc_path:
            lines.append(
                json.dumps({"skip": {"item": str(it), "reason": "no pc_path"}})
            )
            continue
        ops_files = _G["ops_metadata"].get(pc_path)
        bgt_path = _G["bgt_metadata"].get(pc_path)
        if not ops_files or not bgt_path:
            lines.append(
                json.dumps({"skip": {"pc_path": pc_path, "reason": "missing metadata"}})
            )
            continue

        # process_point_cloud returns None; it writes artifacts under modeling_dir
        process_point_cloud(
            pc_path=pc_path,
            pc_ops_files=ops_files,
            bgt_pavements_path=bgt_path,
            args=cli_args,
        )
        lines.append(json.dumps({"modeled": pc_path}))
    return lines


def shutdown() -> None:
    """Shutdown script."""
    logger.info("shutdown()")
