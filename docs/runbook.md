# Operator Runbook

This runbook describes how to run one keyword labeling job from a raw keyword
file to a filterable Chinese review workbook.

## 0. Job Layout

Use one output directory per source file:

```text
outputs/<job-id>/
```

Example:

```text
outputs/tiktok_phrase-match_us_2026-05-26/
```

## 1. Build Intake Fact Table

```bash
python3 scripts/keyword_intake.py \
  "/absolute/path/to/source.xlsx" \
  --sheet "<sheet-name>" \
  --id-prefix "<PREFIX>" \
  --out outputs/<job-id>/intake_fact_table.csv
```

Optional Chinese review copy:

```bash
python3 scripts/keyword_intake.py \
  "/absolute/path/to/source.xlsx" \
  --sheet "<sheet-name>" \
  --id-prefix "<PREFIX>" \
  --locale zh \
  --out outputs/<job-id>/intake_fact_table_zh.csv
```

Output:

```text
outputs/<job-id>/intake_fact_table.csv
outputs/<job-id>/intake_fact_table_zh.csv
```

Rule: intake labels are factual hints only. Semantic annotation does not depend
on these labels.

## 2. Split Into Batches

```bash
python3 scripts/prepare_batches.py \
  outputs/<job-id>/intake_fact_table.csv \
  --out-dir outputs/<job-id> \
  --batch-size 200
```

Output:

```text
outputs/<job-id>/batch_manifest.csv
outputs/<job-id>/batches/batch_001.csv
outputs/<job-id>/batches/batch_002.csv
...
```

## 3. Annotate One Batch

Assign one annotation subagent per batch.

Agent instructions:

```text
Read:
- docs/schemas.md
- docs/batch-policy.md
- skills/intent-grouping/agents/annotation-subagent.md

Input:
outputs/<job-id>/batches/batch_XXX.csv

Output:
outputs/<job-id>/annotations/batch_XXX_annotations.csv

Rules:
- one row per input keyword
- content in Chinese
- field names in English
- semantic annotation is independent from keyword-intake
- if web_verification_required=yes, status must be performed
- conclusion must be concrete Chinese text
```

## 4. Validate Annotation Structure

```bash
python3 scripts/validate_annotation_batch.py \
  --input-batch outputs/<job-id>/batches/batch_XXX.csv \
  --annotation outputs/<job-id>/annotations/batch_XXX_annotations.csv
```

Passing output:

```text
annotation batch validation passed
```

If this fails, fix structure before QA.

## 5. Export Chinese Annotation Sheet

```bash
python3 scripts/export_annotation_zh.py \
  outputs/<job-id>/annotations/batch_XXX_annotations.csv \
  --out outputs/<job-id>/annotations/batch_XXX_annotations_zh.csv
```

## 6. Run Independent QA

Assign a different QA subagent.

Agent instructions:

```text
Read:
- docs/qa-policy.md
- docs/batch-policy.md
- docs/schemas.md
- skills/intent-grouping/agents/qa-subagent.md

Input:
outputs/<job-id>/batches/batch_XXX.csv
outputs/<job-id>/annotations/batch_XXX_annotations.csv

Output:
outputs/<job-id>/qa/batch_XXX_qa.csv
outputs/<job-id>/qa/batch_XXX_qa_problems.csv  # only when problem_count > 0

Do not modify the annotation file.
```

QA pass:

```text
qa_status=pass
problem_count=0
```

Only QA-passed batches can be merged.

## 7. Decide Repair Mode

Use targeted repair when QA only flags a bounded set of rows:

```text
- missing concrete web verification
- label/risk mismatch in specific rows
- a few wrongly classified keywords
```

Use full rerun when QA finds systemic problems:

```text
- template-like annotations across many rows
- repeated intent/risk mistakes
- repeated copying from intake labels
- missing IDs or duplicate IDs
- widespread web_verification_required=yes but not performed
```

## 8. Targeted Repair

Agent instructions:

```text
Input:
outputs/<job-id>/annotations/batch_XXX_annotations.csv
outputs/<job-id>/qa/batch_XXX_qa_problems.csv

Output:
outputs/<job-id>/annotations/batch_XXX_annotations_repaired.csv

Rules:
- preserve all rows and original order
- only modify QA problem rows
- web search every row marked requires_web_search=yes
- if web_verification_required=yes, status must be performed
- rerun validate_annotation_batch.py
```

Then run independent final QA on the repaired file.

## 9. Full Rerun

Agent instructions:

```text
Input:
outputs/<job-id>/batches/batch_XXX.csv
outputs/<job-id>/qa/batch_XXX_qa.csv
outputs/<job-id>/qa/batch_XXX_qa_problems.csv

Output:
outputs/<job-id>/annotations/batch_XXX_annotations_rerun.csv

Rules:
- annotate all 200 rows again
- do not patch only problem rows
- avoid template-like labels
- web search flagged or unstable rows
- rerun validate_annotation_batch.py
```

Then run independent final QA on the rerun file.

## 10. Prepare Merge-Ready Files

After final QA passes, copy the final annotation file into a merge-ready
directory:

```text
outputs/<job-id>/merge_ready_<range>/
```

Example:

```bash
mkdir -p outputs/<job-id>/merge_ready_001_004
cp outputs/<job-id>/annotations/batch_001_annotations_rerun_v3.csv \
  outputs/<job-id>/merge_ready_001_004/batch_001_final.csv
cp outputs/<job-id>/annotations/batch_002_annotations_repaired_v2.csv \
  outputs/<job-id>/merge_ready_001_004/batch_002_final.csv
```

## 11. Build Source Slice For Partial Merge

For a partial merge, create a source slice with exactly the source rows covered
by the merge-ready batches.

For the first 4 batches:

```bash
python3 - <<'PY'
import csv
from pathlib import Path
base=Path("outputs/<job-id>")
source=base/"intake_fact_table.csv"
out=base/"source_first_004_batches.csv"
with source.open(encoding="utf-8") as f:
    reader=csv.DictReader(f)
    fields=reader.fieldnames
    rows=[row for _, row in zip(range(800), reader)]
with out.open("w", encoding="utf-8", newline="") as f:
    writer=csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
PY
```

For a full job, use the full `intake_fact_table.csv` as the source.

## 12. Merge And Check Coverage

```bash
python3 scripts/merge_annotations.py \
  --source outputs/<job-id>/source_first_004_batches.csv \
  --annotations-dir outputs/<job-id>/merge_ready_001_004 \
  --out outputs/<job-id>/merged/full_annotation_details_001_004.csv \
  --coverage-report outputs/<job-id>/merged/coverage_report_001_004.csv
```

Pass condition:

```text
coverage passed for <row-count> rows
```

Do not consolidate or deliver if coverage fails.

## 13. Export Chinese Merged Detail

```bash
python3 scripts/export_annotation_zh.py \
  outputs/<job-id>/merged/full_annotation_details_001_004.csv \
  --out outputs/<job-id>/merged/full_annotation_details_001_004_zh.csv
```

## 14. Build Filterable Review Workbook

```bash
python3 scripts/build_review_workbook.py \
  --detail outputs/<job-id>/merged/full_annotation_details_001_004_zh.csv \
  --qa-summary outputs/<job-id>/merged/qa_summary_001_004.csv \
  --coverage outputs/<job-id>/merged/coverage_report_001_004.csv \
  --out outputs/<job-id>/merged/人工审阅工作簿_001_004.xlsx
```

Every workbook sheet must have filters enabled.

## 15. Current TikTok Example

The first four TikTok batches used these final files:

```text
batch_001_annotations_rerun_v3.csv
batch_002_annotations_repaired_v2.csv
batch_003_annotations_repaired_v3.csv
batch_004_annotations_repaired.csv
```

Merged output:

```text
outputs/tiktok_phrase-match_us_2026-05-26/merged/full_annotation_details_001_004_zh.csv
outputs/tiktok_phrase-match_us_2026-05-26/merged/人工审阅工作簿_001_004.xlsx
```
