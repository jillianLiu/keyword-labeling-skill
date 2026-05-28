#!/usr/bin/env python3
"""Export an annotation CSV with Chinese review-facing headers."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ZH_HEADERS = {
    "original_keyword_id": "原始词ID",
    "keyword": "关键词",
    "volume": "搜索量",
    "semantic_intent_summary": "搜索意图判断",
    "candidate_meaning_label": "候选词义标签",
    "matches_candidate_label": "是否匹配候选标签",
    "risk_entity_platform_type": "风险/实体/平台类型",
    "risk_class": "风险归类",
    "risk_level": "风险等级",
    "needs_human_review": "是否需要人工确认",
    "human_review_reason": "人工确认原因",
    "web_verification_required": "是否需要网络核验",
    "web_verification_status": "网络核验状态",
    "web_verification_query": "网络核验查询",
    "web_verification_conclusion": "网络核验结论",
    "annotation_notes": "标注备注",
    "batch_id": "批次ID",
    "qa_status": "QA状态",
    "annotation_file": "标注文件",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Export annotation CSV with Chinese headers.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    with args.input_csv.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        parser.error("input_csv has no rows")

    source_fields = list(rows[0].keys())
    output_fields = [ZH_HEADERS.get(field, field) for field in source_fields]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({ZH_HEADERS.get(key, key): value for key, value in row.items()})

    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
