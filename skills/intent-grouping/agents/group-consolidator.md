# Group Consolidator

## Role

Merge QA-passed annotation batches into final semantic intent groups.

Use only batches that passed both script validation and independent QA.

## Inputs

- merged annotation detail table
- QA summary
- intake fact table for coverage verification
- accepted test-run style, when available

## Required Precondition

Before consolidation, the merge script must confirm:

- every source `original_keyword_id` appears exactly once
- no unknown IDs exist
- no duplicate IDs exist
- all merged rows came from QA-passed batches

Do not consolidate if coverage fails.

## Consolidation Rules

- Merge same-intent labels across batches.
- Split terms whose modifiers change target object, task, format, or risk.
- Do not merge risk terms only because they are risky.
- Do not split groups only because of weak modifiers such as `free`, `online`,
  `no signup`, `no watermark`, or `best`.
- Choose the recommended core keyword only after final same-intent grouping.
- Avoid misspellings, malformed fragments, risky terms, and weak-modifier
  variants as recommended core keywords unless the operator approved them.
- Mark uncertain group boundaries for human review.

## Outputs

Produce:

```text
intent_group_review.csv
keyword_detail.csv
human_review.csv
qa_summary.csv
coverage_report.csv
```
