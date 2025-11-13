"""Script for planning files for parallel processing pc_prep."""

import argparse
import json
import os
from pathlib import Path

from pc_prep.logger import logger
from pc_prep.tree_prep.metadata_handler import prepare_pc_paths


def main() -> None:
    """Main script."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree_df_path", required=True)
    ap.add_argument("--pc_raw_metadata", required=True)
    ap.add_argument("--pc_raw", required=True)
    ap.add_argument(
        "--out_items_folder", required=True, help="Output folder for item JSON files"
    )
    args = ap.parse_args()

    out_dir = Path(args.out_items_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    pc_paths_abs = prepare_pc_paths(
        tree_df_path=args.tree_df_path,
        pc_metadata_df_path=args.pc_raw_metadata,
        mounted_pc_path=args.pc_raw,
    )

    root = Path(args.pc_raw).resolve()
    written = 0
    for i, p in enumerate(pc_paths_abs, start=1):
        p_abs = Path(p).resolve()
        try:
            rel = os.path.relpath(p_abs, root)
        except Exception as ex:
            logger.warning("Skipping path not under pc_raw: %s (%s)", p_abs, ex)
            continue
        with (out_dir / f"{i:05d}.json").open("w", encoding="utf-8") as f:
            json.dump({"rel_path": rel}, f)
        written += 1

    logger.info("Wrote %d item files to %s", written, out_dir)


if __name__ == "__main__":
    main()
