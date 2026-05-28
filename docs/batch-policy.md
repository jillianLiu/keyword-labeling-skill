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

If structure validation or QA fails, the entire batch is returned for
re-annotation.

The re-annotation must:

- read the original batch input again
- read the QA report
- use web search for words flagged as unclear, risky, entity-like, or wrongly
  labeled
- rewrite the full batch output, not only the failed rows
- run script validation again
- run independent QA again

Partial patching is allowed only when the operator explicitly requests a local
repair.
