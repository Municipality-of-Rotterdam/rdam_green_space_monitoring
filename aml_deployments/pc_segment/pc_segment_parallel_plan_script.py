"""Script for planning files for parallel processing of pc_segment."""

import argparse
import json
from pathlib import Path


def main() -> None:
    """Main script."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--img_metadata", required=True)
    ap.add_argument("--out_items_folder", required=True)
    args = ap.parse_args()

    out_dir = Path(args.out_items_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    # img_metadata is a JSON dict like: { "<tile_key>": {"img_path": "...", "prompt_path": "..."} }
    meta = json.loads(Path(args.img_metadata).read_text(encoding="utf-8"))
    written = 0
    for i, (key, rec) in enumerate(meta.items(), start=1):
        rel = rec.get("img_path")
        if not rel:
            # skip entries with no image
            continue
        # store as RELATIVE path (relative to img_dir)
        item = {"key": key, "img_rel": rel, "prompt_rel": rec.get("prompt_path")}
        (out_dir / f"{i:05d}.json").write_text(json.dumps(item), encoding="utf-8")
        written += 1

    print(f"Wrote {written} segment items to {out_dir}")  # noqa: T201


if __name__ == "__main__":
    main()
