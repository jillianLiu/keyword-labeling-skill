# Schemas

This project uses plain CSV-compatible tables as the shared contract between
scripts, agents, QA, and human review.

## Intake Fact Table

Produced by `keyword-intake`.

Required fields:

```text
original_keyword_id
keyword
source_intent
volume
keyword_difficulty
cpc
near_match_type
near_match_group_id
near_match_group_key
near_match_group_count
comparison_key
morphology_key
action_signal
object_signal
format_signal
modifier_signal
risk_level
risk_label
entity_label
site_fit
site_mismatch_reason
notes
```

Important: these fields are factual hints only. They do not decide semantic
intent in the annotation step.

## Annotation Batch Input

Each batch is a slice of the intake fact table with at most 200 rows.

Required fields:

```text
original_keyword_id
keyword
source_intent
volume
keyword_difficulty
cpc
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

The annotation agent may read all fields, but must decide semantic meaning from
the keyword itself and search-intent reasoning, not from intake labels.

## Annotation Batch Output

One output row per input keyword.

Required fields:

```text
original_keyword_id
keyword
volume
semantic_intent_summary
candidate_meaning_label
matches_candidate_label
risk_entity_platform_type
risk_class
risk_level
needs_human_review
human_review_reason
web_verification_required
web_verification_status
web_verification_query
web_verification_conclusion
annotation_notes
```

Rules:

- `original_keyword_id` must match the input exactly.
- `keyword` must preserve the input keyword text.
- `semantic_intent_summary` must explain the likely search intent in one
  concrete sentence.
- `candidate_meaning_label` is provisional and can be merged later.
- `web_verification_required` is `yes` or `no`.
- If `web_verification_required=yes`, the verification fields must be filled.

## QA Report

One QA report per annotation batch.

Required fields:

```text
batch_id
qa_status
checked_rows
problem_count
qa_notes
```

Problem rows table:

```text
original_keyword_id
keyword
current_label
problem
recommended_fix
requires_web_search
suggested_web_query
```

Allowed `qa_status` values:

```text
pass
fail
```

If `qa_status=fail`, the whole batch must be returned for re-annotation.

## Merged Annotation Table

Produced only from batches that passed QA.

Required fields are the same as annotation batch output, plus:

```text
batch_id
qa_status
```

The merge script must verify every source `original_keyword_id` appears exactly
once in the merged output.

## Intent Group Review Table

One row per final semantic intent group.

Required fields:

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

`preliminary_page_recommendation` is only a review signal. It is not final page
planning.

## Keyword Detail Table

One row per original keyword.

Required fields:

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
