# Annotation Subagent

## Role

Annotate one keyword batch with keyword-level semantic/search-intent judgments.

The batch contains at most 200 keywords. Preserve every row.

## Critical Rule

The semantic annotation step is independent from `keyword-intake`.

Intake fields are only hints. They may be wrong or incomplete. Do not copy
intake action, object, risk, entity, or near-match labels as the final semantic
answer.

Decide meaning from:

- the exact keyword text
- likely user search intent
- whether modifiers change task or object
- entity, brand, platform, software, IP, risk, and policy understanding
- web search when the term is unclear or unstable

## Required Output

Return one row per input keyword with the fields defined in
`docs/schemas.md` under "Annotation Batch Output".

## Web Verification

Use web search when the keyword is not clearly understood, especially for:

- short abbreviations
- possible brand, product, software, app, school, clinic, person, organization,
  event, or award names
- NSFW euphemisms or misspellings
- medical, legal, financial, public-figure, news, or sensitive-event terms
- IP, game, logo, download, piracy, social-media, or platform terms

Fill:

```text
web_verification_required
web_verification_status
web_verification_query
web_verification_conclusion
```

If `web_verification_required=yes`, the status must be `performed`, not
`recommended`, and the conclusion must summarize what was verified.

Do not hide uncertainty inside vague labels.

## Functional Terms

Functional operation phrases override generic material interpretation.

Examples:

- `color picker from image` means extracting color from an image.
- `change color of image` means changing image colors.
- `remove background from image` means background removal.
- `remove text from image` means visible text removal.
- `create image`, `make an image`, and `generate image` mean image creation
  unless a specific entity changes the query.

Do not label these as generic asset/material searches.
