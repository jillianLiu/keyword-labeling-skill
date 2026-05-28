# Output Contract

## Formal Outputs

Formal human-review outputs should use Chinese column names and Chinese review
notes by default.

These files are formal handoff artifacts:

```text
intent_group_review.csv
keyword_detail.csv
human_review.csv
qa_summary.csv
coverage_report.csv
```

Optional:

```text
review_workbook.xlsx
```

## Intermediate Outputs

These files can be regenerated:

```text
batches/batch_*.csv
annotations/batch_*_annotations.csv
qa/batch_*_qa.csv
merged/full_annotation_details.csv
```

## Required Coverage Check

After merging annotation batches, run a script-level coverage check against the
source intake fact table.

The check must verify:

- every source `original_keyword_id` appears in the merged annotation table
- no merged annotation row uses an unknown ID
- no ID appears more than once
- source row count equals merged row count

If coverage fails, do not proceed to global intent group consolidation.

## Human Review Outputs

`human_review.csv` should contain only rows that need operator attention:

- uncertain semantic boundaries
- risky or policy-sensitive terms
- platform/brand/competitor decisions
- unclear entities
- low-confidence group merges
- recommended core keywords that may be risky, unnatural, or weak-modifier
  variants

Recommended Chinese review-facing file names:

```text
词义组审阅表.csv
关键词明细表.csv
人工确认表.csv
QA汇总表.csv
覆盖检查表.csv
```
