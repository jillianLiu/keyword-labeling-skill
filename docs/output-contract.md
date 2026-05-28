# Output Contract

## Formal Outputs

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
