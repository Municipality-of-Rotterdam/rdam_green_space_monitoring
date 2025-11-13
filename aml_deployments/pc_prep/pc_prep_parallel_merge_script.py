"""Script for merging pc_prep results."""

import argparse
import json
from pathlib import Path


def main() -> None:
    """Main script."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--partial", required=True, help="JSONL from append_row_to")
    ap.add_argument("--img_metadata", required=True)
    ap.add_argument("--pc_metadata", required=True)
    ap.add_argument("--bgt_metadata", required=True)
    args = ap.parse_args()

    img_meta, pc_meta, bgt_meta = {}, {}, {}

    partial_path = Path(args.partial)
    # file may be named "job_output_file" under parallel step
    with partial_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            # row == {"pc": {...}, "img": {...}, "bgt": {...}}
            pc_meta.update(row.get("pc", {}))
            img_meta.update(row.get("img", {}))
            bgt_meta.update(row.get("bgt", {}))

    # Write final dicts (your original component format)
    for out, data in [
        (args.pc_metadata, pc_meta),
        (args.img_metadata, img_meta),
        (args.bgt_metadata, bgt_meta),
    ]:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as jf:
            json.dump(data, jf, indent=4)
        print(f"Wrote {out}")  # noqa: T201


if __name__ == "__main__":
    main()
