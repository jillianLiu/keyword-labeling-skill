# Workflow Notes

## Boundary

This project stops at keyword labeling and semantic intent grouping.

Out of scope:

- final SEO page planning
- landing-page copywriting
- localization
- CMS export
- image generation
- publish review

## Operator Flow

1. Put the raw keyword file in `data/input/`.
2. Run `keyword-intake` to produce a fact table.
3. Review row counts and deterministic labels.
4. Split the fact table into batches of at most 200 keywords.
5. Run a small `intent-grouping` test sample.
6. Accept or revise the grouping style.
7. Run annotation subagents batch by batch.
8. Run independent QA for every annotation batch.
9. If a batch fails QA, re-annotate the whole batch and use web search for
   terms QA flagged as unsuitable, unclear, risky, or entity-like.
10. Merge only QA-passed batches.
11. Run script coverage checks against the source fact table to catch missing,
    duplicated, or unknown keyword IDs.
12. Consolidate final intent groups.
13. Review group and keyword detail tables.

## Required Human Decisions

The operator decides:

- whether uncertain groups should be merged or split
- whether risky groups are allowed
- whether platform, brand, or competitor terms fit the project
- whether recommended core keywords are acceptable
- whether grouped results can move into page planning

## Critical Rules

- Semantic annotation does not depend on `keyword-intake` labels. Intake labels
  are hints only.
- Every annotation batch has at most 200 keywords.
- Failed batches are returned as whole batches, not patched row by row by
  default.
- Merge cannot proceed until all included batches pass QA.
- Final consolidation cannot proceed until merge coverage passes.
