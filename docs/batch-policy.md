# Batch Policy

## Batch Size

Keyword-level semantic annotation must be split into batches of at most 200
keywords.

Use smaller batches when the source contains many:

- unknown entities
- brands, platforms, or software names
- medical, legal, financial, or public-figure terms
- NSFW, piracy, IP, or policy-sensitive terms
- short ambiguous phrases

## Batch Naming

Use stable, ordered names:

```text
batch_001.csv
batch_002.csv
batch_003.csv
```

Create a manifest:

```text
batch_id
input_file
row_count
first_original_keyword_id
last_original_keyword_id
status
```

## Independence From Intake Labels

The annotation step may use intake fields as context, but must not treat them
as semantic truth.

The annotation agent must decide search intent from:

- the exact keyword text
- likely user intent
- modifier meaning
- entity/risk/platform understanding
- web search when the term is unclear or risky

If intake tags conflict with semantic judgment, the annotation should explain
the correction.

## Failed Batch Handling

If structure validation fails, the entire batch is returned for re-annotation.

If semantic QA fails because of systemic annotation problems, the entire batch
is returned for re-annotation.

Systemic problems include:

- missing or duplicate keyword IDs
- many rows copied mechanically from intake labels
- repeated functional-vs-material misclassification
- repeated risk/entity/platform misclassification
- vague labels that hide uncertainty across the batch

The full-batch re-annotation must:

- read the original batch input again
- read the QA report
- use web search for words flagged as unclear, risky, entity-like, or wrongly
  labeled
- rewrite the full batch output, not only the failed rows
- run script validation again
- run independent QA again

If semantic QA fails only because a bounded set of rows needs web verification
or a more concrete verification conclusion, targeted repair is allowed. The
repair must:

- preserve all rows and original order
- only modify rows listed in the QA problems file
- use web search for each row marked `requires_web_search=yes`
- set `web_verification_status=performed` when verification is required
- rerun script validation on the repaired full annotation file
- receive independent QA again
