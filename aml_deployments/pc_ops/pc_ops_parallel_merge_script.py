"""Merge ops metadata."""

import argparse
import glob
import json
import os


def main() -> None:
    """Main script."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--partials_dir", required=True)
    ap.add_argument("--final_path", required=True)
    args = ap.parse_args()

    merged = {}
    for p in sorted(glob.glob(os.path.join(args.partials_dir, "*.json"))):
        with open(p, "r") as f:
            try:
                part = json.load(f)
                if isinstance(part, dict):
                    merged.update(part)
            except Exception as e:
                print(f"Exception: {e}")  # noqa: T201
                # skip malformed
    os.makedirs(os.path.dirname(args.final_path), exist_ok=True)
    with open(args.final_path, "w") as f:
        json.dump(merged, f, indent=4)
    print(f"Merged {len(merged)} entries into {args.final_path}")  # noqa: T201


if __name__ == "__main__":
    main()
