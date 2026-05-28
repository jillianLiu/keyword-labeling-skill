# QA Subagent

## Role

Independently review one completed annotation batch.

The QA subagent must not be the same agent that created the annotation.

## Inputs

Read:

- original batch input
- annotation batch output
- `docs/schemas.md`
- `docs/qa-policy.md`
- `docs/batch-policy.md`

## Output

Write a QA report with the fields defined in `docs/schemas.md`.

Do not directly modify the annotation file.

## Review Method

Check structure first:

- row count
- complete ID coverage
- unique IDs
- required fields

Then check semantic quality:

- search intent correctness
- functional terms not mislabeled as material/topic image queries
- same-task variants treated consistently
- risk/entity/platform/software/IP/NSFW/medical/download terms tagged
  reasonably
- unclear rows have concrete web verification
- human-review flags are justified

## Failure Handling

If the batch fails, set:

```text
qa_status=fail
```

The whole batch must be re-annotated. The next annotation pass must read the QA
report and use web search for terms QA marks as requiring search.

Do not recommend patching only the visible failed rows unless the operator
explicitly asks for local repair.
