"""Script for planning files for parallel processing of tree_modeling."""

import argparse
import json
from pathlib import Path


def main() -> None:
    """Main script."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--ops_metadata", required=True)
    ap.add_argument("--out_items_folder", required=True)
    args = ap.parse_args()

    ops = json.loads(Path(args.ops_metadata).read_text(encoding="utf-8"))
    out = Path(args.out_items_folder)
    out.mkdir(parents=True, exist_ok=True)

    for i, pc_path in enumerate(ops.keys(), start=1):
        (out / f"{i:05d}.json").write_text(
            json.dumps({"pc_path": pc_path}), encoding="utf-8"
        )
    print(f"Wrote {len(ops)} items -> {out}")  # noqa: T201


if __name__ == "__main__":
    main()
