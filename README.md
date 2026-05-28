# keyword-labeling-skill

Independent skills for processing, labeling, and grouping large keyword lists.

This project is intentionally separated from product-specific SEO copywriting,
localization, image generation, and publishing workflows. It focuses only on:

1. importing raw keyword tables,
2. preserving every keyword row,
3. adding deterministic factual labels,
4. verifying keyword-level search intent,
5. grouping keywords by semantic intent,
6. producing human-reviewable classification workbooks.

## Workflow

```text
raw keyword export
-> keyword-intake
-> split into batches of up to 200 keywords
-> intent-grouping
-> independent QA
-> merge QA-passed batches
-> coverage check
-> human review
```

## Skills

### keyword-intake

Use for raw CSV/XLSX/TSV keyword exports. It normalizes schema, creates stable
row IDs, keeps original keywords unchanged, marks near variants, and adds
deterministic signals such as action, object, format, modifier, risk, entity,
and site-fit labels.

This skill must not decide final semantic groups, page candidates, final core
keywords, or whether a page should be created.

### intent-grouping

Use after `keyword-intake`. It performs keyword-level search-intent
verification, merges same-intent variants, tags risk/entity/platform issues,
selects group-level core keyword candidates, and creates review tables.

The semantic annotation step is independent from `keyword-intake` labels.
Intake output is a factual hint table, not a semantic decision.

This skill stops at intent groups. It does not create final SEO pages or write
marketing copy.

## Expected Directories

```text
data/input/     raw keyword files or small test samples
outputs/        generated fact tables, annotations, and review workbooks
docs/           operator notes and accepted style references
scripts/        deterministic batch, validation, merge, and workbook helpers
skills/         Codex skill definitions
```

## Review Invariants

- Preserve every original keyword.
- Never silently drop risky, off-topic, duplicated, or malformed rows.
- Treat deterministic labels as hints, not final semantic truth.
- Verify every keyword's meaning before final grouping.
- Re-annotate failed batches as whole batches, using web search for unsuitable
  or unclear terms flagged by QA.
- After merging batches, run script coverage checks for missing, duplicate, or
  unknown keyword IDs.
- Mark uncertain entities, risky terms, and ambiguous queries for human review.

## Core References

- `docs/schemas.md`: table contracts
- `docs/batch-policy.md`: 200-keyword batch rule and failed-batch handling
- `docs/qa-policy.md`: independent QA requirements
- `docs/output-contract.md`: final and intermediate outputs
