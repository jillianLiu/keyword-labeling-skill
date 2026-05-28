#!/usr/bin/env python3
"""Validate one annotation batch against its source batch and optional QA report."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


REQUIRED_ANNOTATION_FIELDS = [
    "original_keyword_id",
    "keyword",
    "volume",
    "semantic_intent_summary",
    "candidate_meaning_label",
    "risk_entity_platform_type",
    "risk_class",
    "risk_level",
    "needs_human_review",
    "human_review_reason",
    "web_verification_required",
]

WEB_VERIFICATION_FIELDS = [
    "web_verification_status",
    "web_verification_query",
    "web_verification_conclusion",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate annotation batch structure and coverage.")
    parser.add_argument("--input-batch", type=Path, required=True)
    parser.add_argument("--annotation", type=Path, required=True)
    parser.add_argument("--qa-report", type=Path)
    args = parser.parse_args()

    source_rows = read_rows(args.input_batch)
    annotation_rows = read_rows(args.annotation)
    errors: list[str] = []

    if not source_rows:
        errors.append("input batch has no rows")
    if not annotation_rows:
        errors.append("annotation has no rows")

    if source_rows and "original_keyword_id" not in source_rows[0]:
        errors.append("input batch missing original_keyword_id")
    if annotation_rows:
        missing_fields = [
            field
            for field in REQUIRED_ANNOTATION_FIELDS + WEB_VERIFICATION_FIELDS
            if field not in annotation_rows[0]
        ]
        if missing_fields:
            errors.append(f"annotation missing required fields: {', '.join(missing_fields)}")

    if not errors:
        source_ids = [row["original_keyword_id"] for row in source_rows]
        annotation_ids = [row["original_keyword_id"] for row in annotation_rows]
        source_set = set(source_ids)
        annotation_set = set(annotation_ids)
        annotation_counts = Counter(annotation_ids)

        missing = sorted(source_set - annotation_set)
        unknown = sorted(annotation_set - source_set)
        duplicate = sorted(keyword_id for keyword_id, count in annotation_counts.items() if count > 1)
        if len(source_rows) != len(annotation_rows):
            errors.append(f"row count mismatch: input={len(source_rows)} annotation={len(annotation_rows)}")
        if missing:
            errors.append(f"missing ids: {';'.join(missing)}")
        if unknown:
            errors.append(f"unknown ids: {';'.join(unknown)}")
        if duplicate:
            errors.append(f"duplicate annotation ids: {';'.join(duplicate)}")

        for row in annotation_rows:
            row_id = row.get("original_keyword_id", "")
            for field in REQUIRED_ANNOTATION_FIELDS:
                value = (row.get(field) or "").strip()
                if not value:
                    errors.append(f"{row_id}: blank required field {field}")
            if (row.get("web_verification_required") or "").strip().lower() in {"yes", "true", "1"}:
                status = (row.get("web_verification_status") or "").strip().lower()
                if status != "performed":
                    errors.append(f"{row_id}: web verification required but status is not performed")
                for field in WEB_VERIFICATION_FIELDS:
                    if not (row.get(field) or "").strip():
                        errors.append(f"{row_id}: web verification required but {field} is blank")

    if args.qa_report:
        qa_rows = read_rows(args.qa_report)
        if not qa_rows:
            errors.append("qa report has no rows")
        else:
            status = (qa_rows[0].get("qa_status") or "").strip().lower()
            if status not in {"pass", "通过"}:
                errors.append(f"qa_status is not pass: {status or '<blank>'}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("annotation batch validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
