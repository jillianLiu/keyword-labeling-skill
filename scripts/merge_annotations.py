#!/usr/bin/env python3
"""Merge QA-passed annotation batches and report source coverage."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
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
    parser = argparse.ArgumentParser(description="Merge annotation CSVs and verify source keyword coverage.")
    parser.add_argument("--source", type=Path, required=True, help="intake fact table CSV")
    parser.add_argument("--annotations-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--coverage-report", type=Path, required=True)
    args = parser.parse_args()

    source_rows = read_rows(args.source)
    if not source_rows:
        parser.error("--source has no rows")
    if "original_keyword_id" not in source_rows[0]:
        parser.error("--source must include original_keyword_id")

    annotation_files = sorted(args.annotations_dir.glob("*.csv"))
    if not annotation_files:
        parser.error("--annotations-dir contains no CSV files")

    merged: list[dict[str, str]] = []
    fieldnames: list[str] | None = None
    for annotation_file in annotation_files:
        rows = read_rows(annotation_file)
        if not rows:
            continue
        if "original_keyword_id" not in rows[0]:
            parser.error(f"{annotation_file} must include original_keyword_id")
        if fieldnames is None:
            fieldnames = list(rows[0].keys())
        for row in rows:
            row = dict(row)
            row.setdefault("annotation_file", annotation_file.name)
            merged.append(row)

    if fieldnames is None:
        parser.error("annotation files have no rows")
    if "annotation_file" not in fieldnames:
        fieldnames.append("annotation_file")

    source_ids = [row["original_keyword_id"] for row in source_rows]
    merged_ids = [row["original_keyword_id"] for row in merged]
    source_set = set(source_ids)
    merged_set = set(merged_ids)
    merged_counts = Counter(merged_ids)

    missing = sorted(source_set - merged_set)
    unknown = sorted(merged_set - source_set)
    duplicate = sorted(keyword_id for keyword_id, count in merged_counts.items() if count > 1)

    coverage_rows = [
        {"check": "source_row_count", "result": str(len(source_rows)), "status": "info"},
        {"check": "merged_row_count", "result": str(len(merged)), "status": "info"},
        {"check": "missing_source_ids", "result": ";".join(missing), "status": "fail" if missing else "pass"},
        {"check": "unknown_merged_ids", "result": ";".join(unknown), "status": "fail" if unknown else "pass"},
        {"check": "duplicate_merged_ids", "result": ";".join(duplicate), "status": "fail" if duplicate else "pass"},
    ]

    write_rows(args.out, fieldnames, merged)
    write_rows(args.coverage_report, ["check", "result", "status"], coverage_rows)

    failed = missing or unknown or duplicate or len(source_rows) != len(merged)
    if failed:
        print("coverage failed")
        return 1

    print(f"coverage passed for {len(merged)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
