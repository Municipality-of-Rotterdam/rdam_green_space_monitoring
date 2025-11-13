"""Script for merging of parallel processing results for tree_modeling."""

import argparse
import json
from pathlib import Path


def main() -> None:
    """Main script."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--partial", required=True)
    ap.add_argument("--modeling_index", required=True)
    args = ap.parse_args()

    modeled = []
    for line in Path(args.partial).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            row = json.loads(s)
        except json.JSONDecodeError:
            continue
        if "modeled" in row:
            modeled.append(row["modeled"])

    Path(args.modeling_index).parent.mkdir(parents=True, exist_ok=True)
    Path(args.modeling_index).write_text(
        json.dumps({"modeled": modeled}, indent=4), encoding="utf-8"
    )
    print(f"Wrote {len(modeled)} modeled keys -> {args.modeling_index}")  # noqa: T201


if __name__ == "__main__":
    main()
