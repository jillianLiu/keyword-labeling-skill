#!/usr/bin/env python3
"""Split a keyword fact table into fixed-size annotation batches."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Split keyword fact table into annotation batches.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=200)
    args = parser.parse_args()

    if args.batch_size < 1 or args.batch_size > 200:
        parser.error("--batch-size must be between 1 and 200")

    rows = read_rows(args.input_csv)
    if not rows:
        parser.error("input_csv has no rows")

    fieldnames = list(rows[0].keys())
    if "original_keyword_id" not in fieldnames:
        parser.error("input_csv must include original_keyword_id")

    manifest: list[dict[str, str]] = []
    for index in range(0, len(rows), args.batch_size):
        batch_rows = rows[index : index + args.batch_size]
        batch_no = len(manifest) + 1
        batch_id = f"batch_{batch_no:03d}"
        batch_file = args.out_dir / "batches" / f"{batch_id}.csv"
        write_rows(batch_file, fieldnames, batch_rows)
        manifest.append(
            {
                "batch_id": batch_id,
                "input_file": str(batch_file),
                "row_count": str(len(batch_rows)),
                "first_original_keyword_id": batch_rows[0]["original_keyword_id"],
                "last_original_keyword_id": batch_rows[-1]["original_keyword_id"],
                "status": "prepared",
            }
        )

    write_rows(
        args.out_dir / "batch_manifest.csv",
        [
            "batch_id",
            "input_file",
            "row_count",
            "first_original_keyword_id",
            "last_original_keyword_id",
            "status",
        ],
        manifest,
    )
    print(f"wrote {len(manifest)} batches for {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
