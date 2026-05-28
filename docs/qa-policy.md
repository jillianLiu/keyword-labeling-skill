# QA Policy

QA is a separate semantic review step for annotation batches.

## Role

The QA subagent must not be the same agent that created the annotation batch.
It reads:

- the batch input
- the annotation output
- relevant project rules and schemas

It does not directly modify the annotation output.

## QA Scope

QA checks both structure and meaning:

- row count equals input row count
- every input `original_keyword_id` appears exactly once
- required fields are not empty
- semantic intent was understood correctly
- functional phrases were not mislabeled as generic asset/material queries
- same-task spelling, singular/plural, and word-order variants are compatible
- brand, platform, competitor, software, IP, NSFW, medical, download, piracy,
  and sensitive terms are tagged reasonably
- unclear terms have concrete web verification fields
- human-review flags are justified

## Web Search In QA

QA should recommend web search when a term is:

- an unknown abbreviation
- a possible brand, software, product, person, organization, event, school, or
  clinic
- a possible NSFW euphemism or misspelling
- a medical, legal, financial, public-figure, news, or sensitive-event query
- an IP, logo, download, piracy, platform, or social-media query where intent
  is unclear

When QA fails a row for this reason, the QA report must include
`requires_web_search=yes` and a suggested query.

## Pass / Fail Rule

Use:

```text
qa_status=pass
qa_status=fail
```

Fail the whole batch when:

- any input keyword is missing
- any duplicate ID exists
- required fields are blank
- repeated semantic mistakes show the annotator is following intake labels
  mechanically
- obvious functional terms are labeled as material/image lookup
- risky or entity-like terms are not flagged or verified
- unclear rows are hidden under vague labels

If QA fails, the whole batch must be re-annotated with the QA report as input.
The re-annotation must use web search for the terms QA flagged as requiring it.
