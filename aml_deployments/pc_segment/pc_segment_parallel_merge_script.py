"""Script for merging of parallel pc_segment results."""

import argparse
import json
from pathlib import Path
from typing import Dict


def main() -> None:
    """Main script."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--partial", required=True)
    ap.add_argument("--segment_metadata", required=True)
    args = ap.parse_args()

    out: Dict[str, str] = {}
    partial_path = Path(args.partial)

    with partial_path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                row = json.loads(s)
            except json.JSONDecodeError:
                continue
            out.update(row)

    Path(args.segment_metadata).parent.mkdir(parents=True, exist_ok=True)
    Path(args.segment_metadata).write_text(json.dumps(out, indent=4), encoding="utf-8")
    print(f"Merged {len(out)} entries -> {args.segment_metadata}")  # noqa: T201


if __name__ == "__main__":
    main()
