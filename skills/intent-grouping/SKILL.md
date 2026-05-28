---
name: intent-grouping
description: Build semantic intent groups from prepared keyword fact tables. Use this after keyword-intake when the user wants to verify every keyword's search meaning, group keywords by intent, handle misspellings and near variants, tag risk/entity/platform issues, select group-level core keyword candidates, or produce human-reviewable keyword classification tables.
---

# intent-grouping

## Purpose

Turn a prepared keyword fact table into human-reviewable semantic intent groups.

This skill comes after `keyword-intake`. It uses the factual labels and
near-match hints from intake, but it does not treat them as final semantic
truth.

The semantic annotation step is independent from `keyword-intake` labels.
Intake output can guide review, but it must not decide final meaning.

Do not generate final page candidates in this skill. Stop at intent-group
classification tables and coverage checks.

Use Chinese column names and Chinese review notes for final human-review
outputs unless the operator explicitly requests English.

## Required Input

Use the output from `keyword-intake`.

Expected fields include:

```text
original_keyword_id
keyword
source_intent
volume
keyword_difficulty
cpc
near_match_type
near_match_group_id
action_signal
object_signal
format_signal
modifier_signal
risk_level
risk_label
entity_label
site_fit
site_mismatch_reason
```

Never hardcode keyword counts from previous runs.

## Core Principles

1. Preserve every original keyword.
2. Group by meaning and search intent, not by string similarity alone.
3. Treat misspellings, word-order variants, singular/plural variants, and near
   duplicates as same-intent only when users are searching for the same thing.
4. Intake labels are hints, not final conclusions.
5. Every keyword must receive search-intent verification.
6. Risk, entity, and platform issues are tagged during grouping, but risk terms
   are not pooled into one generic risk group.
7. Choose group-level core keyword candidates only after same-intent grouping.
8. Weak modifiers do not create groups by default.
9. Use precise, human-readable group names.
10. Mark unclear or unstable cases for human confirmation.

## Test Runs

Before a full run, ask whether the operator wants a test sample.

Default test size:

```text
first 50 keywords by source order or by volume, depending on the goal
```

Do not launch a full run until the operator accepts the test quality or
explicitly asks to skip testing.

The accepted test output becomes the style reference for the full run.

## Step 1: Keyword-Level Search-Intent Verification

Every keyword must be verified for search meaning.

For large files, split keyword-level verification into subagent batches of at
most 200 keywords each. This is a hard ceiling, not a target to exceed for
throughput. Smaller batches are preferred when the keyword set contains many
ambiguous entities, brands, tools, medical terms, NSFW terms, platform terms,
or IP/download terms.

The first `keyword-intake` step is only deterministic cleaning, near-match
grouping, and factual signal extraction. Its output is a hint table, not a
semantic answer. The second intent-grouping step is where human-level semantic
understanding happens.

Use `agents/annotation-subagent.md` for per-batch annotation rules.

Verification means determining:

- what users likely want when searching this exact keyword
- whether a modifier changes the target object or task
- whether the keyword matches the current group intent
- whether there is brand, platform, competitor, IP, adult, piracy, sensitive,
  medical, legal, financial, public-figure, or unrelated-entity meaning
- whether the keyword needs web verification
- whether the keyword needs human confirmation

Web verification is required for:

- unknown abbreviations or short entities
- brand-like, product-like, software, app, tool, school, clinic, organization,
  award, event, or person names
- possible NSFW misspellings or euphemisms
- possible medical, legal, financial, public-figure, news, or sensitive-event
  queries
- IP, game, platform, social-media, logo, or download terms where copyright,
  navigation intent, or platform policy is unclear
- any term where the agent cannot explain the search intent in one concise,
  concrete sentence

Do not hide uncertainty behind a vague low-confidence label. If a keyword is
unclear, the annotation must say why it is unclear, whether web verification is
recommended or performed, and what the verification conclusion is.

Explicit functional phrases take priority over generic image-material
interpretations. For example:

- `color selector from image`, `color picker from image`, `color finder from
  image`, and `hex color from image` mean extracting or identifying colors from
  an image.
- `change color of image`, `change colors of image`, `image color changer`,
  `image colour changer`, and `recolor image` mean changing or replacing image
  colors. Singular and plural color/color(s) variants are same-intent unless
  another modifier changes the task.
- `remove image background`, `remove background from image`, `background image
  remover`, and misspellings such as `backround remover` mean background
  removal or transparent-background creation.
- `remove text from image`, `delete text from image`, and `text remover from
  image` mean removing visible text from an image.
- `create image`, `create an image`, `make an image`, `generate image`, and
  `ai generated image` mean image generation or image creation unless the query
  clearly refers to another product/entity.

Functional operation terms must not be labeled as `asset/material`,
`specific-topic image`, or generic visual reference queries.

## Batch QA Gate

Each annotation batch must pass two gates before it can be merged:

1. Script/structure validation: row count, unique original keyword IDs,
   required non-empty fields, and coverage.
2. Independent semantic QA by a separate QA subagent.

The QA subagent must not be the same agent that annotated the batch. It must
read both the batch input and annotation output, and it must not modify the
annotation file. It writes a QA report containing:

```text
batch_id
qa_status: 通过/不通过
checked_rows
problem_count
problem_rows table:
  original_keyword_id
  keyword
  current_label
  problem
  recommended_fix
qa_notes
```

The QA subagent checks semantic correctness, not only formatting:

- whether the search intent was understood correctly
- whether functional terms were mislabeled as generic image material or topic
  images
- whether singular/plural, spelling, and word-order variants were treated as
  same-intent when they mean the same user task
- whether brand, software, medical, IP, NSFW, platform, download, and entity
  terms are tagged reasonably
- whether unclear terms that require web verification have a concrete
  verification reason and conclusion
- whether risk and human-review flags are reasonable

If QA status is `不通过`, do not merge the batch. Reassign the entire batch for
re-annotation or full-batch correction. The re-annotation must use web search
for terms QA marked as unsuitable, unclear, risky, entity-like, or wrongly
labeled. Then run script validation and independent QA again. Do not only patch
a few visible rows unless the operator explicitly requests a local repair.

Use `agents/qa-subagent.md` and `docs/qa-policy.md` for QA rules.

## Merge Coverage Gate

After QA-passed annotation batches are merged, run a script-level coverage
check against the source intake fact table.

The merge cannot proceed to global consolidation unless the script confirms:

- every source `original_keyword_id` appears exactly once
- no source keyword is missing
- no duplicate IDs exist
- no merged row uses an unknown ID
- every merged row came from a QA-passed batch

## Step 2: Global Intent Group Consolidation

After keyword-level verification, consolidate candidate meaning labels into
final groups.

Use `agents/group-consolidator.md` for global consolidation rules.

This step should:

- merge same-intent labels across batches
- split terms whose modifiers change target object, format, or task
- select stable final group IDs
- create human-readable group names
- choose a recommended core keyword from the final same-intent group by volume
  and naturalness
- preserve every original keyword in exactly one detail row
- mark uncertain boundaries with `needs_human_review = yes`

## Group-Level Review Table

Create one row per semantic intent group:

```text
category
needs_human_review
human_review_reason
intent_group_id
intent_group_name
recommended_core_keyword
core_keyword_volume
group_keywords
keyword_count
risk_entity_platform_type
risk_level
search_verification_summary
preliminary_page_recommendation
url_slug
notes
```

Rules:

- `group_keywords` format is `keyword(volume)` separated by semicolons.
- `recommended_core_keyword` should be the highest-volume natural keyword in
  the verified same-intent group.
- Do not choose misspellings, malformed repetitions, risky terms, or weak
  modifier variants as core by default.
- `preliminary_page_recommendation` is only a review signal.

## Keyword Detail Table

Create one row per original keyword:

```text
needs_human_review
human_review_reason
intent_group_id
keyword
volume
search_verification_conclusion
matches_group_intent
risk_entity_platform_type
risk_class
risk_level
source_intent
keyword_difficulty
cpc
near_match_group_id
candidate_meaning_label
notes
```

The detail table exists for traceability and debugging.

## Recommended Categories

Use broad review-stage categories:

```text
tool/function
asset/material
tutorial
blog/informational
comparison/list
brand/competitor
risk-review
do-not-build
undecided
```

Do not treat these as final page templates.

## Quality Checks

Before returning output, verify:

- every input `original_keyword_id` appears exactly once
- output detail row count equals input row count
- no required group or detail fields are blank
- same-intent variants were grouped before core selection
- explicit operation phrases were not mislabeled as generic asset searches
- risky and ambiguous terms are marked for review
- no final page plan or marketing copy was generated
