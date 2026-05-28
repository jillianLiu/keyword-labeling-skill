---
name: keyword-intake
description: Import raw keyword exports and produce a complete keyword fact table before semantic intent grouping. Use this when the user provides CSV, TSV, XLSX, Semrush exports, or large keyword lists and asks to clean, preserve, dedupe, tag, or prepare keywords for later labeling.
---

# keyword-intake

## Purpose

Turn a raw keyword export into a complete, reviewable keyword fact table.

This skill owns deterministic intake and factual tagging only. It must not
decide final semantic groups, final page candidates, final core keywords, or
final secondary keyword matches.

The main invariant is coverage: every original keyword row must be preserved.
If a keyword is risky, off-topic, near-matched, misspelled, or unsuitable, keep
it and label why instead of deleting it.

## Inputs

Accept spreadsheet files with common keyword fields:

```text
Keyword
Intent
Volume
Keyword Difficulty
CPC
```

Map differing source column names to:

```text
original_keyword_id
keyword
source_intent
volume
keyword_difficulty
cpc
```

Generate stable row IDs when the source file does not include IDs.

## Outputs

Create a fact table with one row per original keyword:

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

Use localized column labels when the operator requests them.

## Deterministic Rules

1. Preserve the original keyword exactly as provided.
2. Create normalized internal keys for matching:
   - lowercase
   - trim leading/trailing whitespace
   - collapse repeated spaces
   - normalize punctuation spacing
3. Do not remove modifiers such as `free`, `online`, `best`, `top`,
   `no signup`, or `no watermark`.
4. Mark near matches but do not merge or delete rows.
5. Keep volume, difficulty, CPC, and source intent unchanged.
6. Keep deterministic labels conservative. When unsure, leave a note for
   semantic verification.

## Near-Match Labels

Use one unified near-match field set:

```text
unique
format_near
morphology_near
format_and_morphology_near
```

Definitions:

- `format_near`: equivalent after conservative case, spacing, or punctuation
  normalization.
- `morphology_near`: likely singular/plural or simple word-form variants.
- `format_and_morphology_near`: both conditions are involved.
- `unique`: no near-match group was found.

Near matches are hints for later semantic grouping. They are not automatic
duplicates.

## Factual Signals

Tag obvious factual signals without deciding pages or final meaning.

Common action signals:

```text
generate
edit
remove-background
change-background
transparent
resize
crop
compress
upscale
enhance
unblur
convert
ocr
translate
search
reverse-search
detect
color-pick
palette
upload-host
remove-object
remove-text
recolor
change-color
```

Common object signals:

```text
image
photo
picture
logo
icon
background
avatar
portrait
stock
wallpaper
product
```

Common format signals:

```text
png
jpg/jpeg
webp
svg/vector
pdf
gif
heic
```

Common modifier signals:

```text
free
online
no signup
no watermark
best/top
api
app/mobile
bulk
download
commercial
```

## Risk And Entity Tags

Keep risk level and reason separate:

```text
risk_level: none | low | medium | high
risk_label: adult/nsfw | ip/trademark | sensitive | policy | piracy | unknown
entity_label: competitor | platform/navigation | brand/entity | off-topic entity
```

These are review signals, not final page decisions.

## Quality Checks

Before returning output, verify:

- output row count equals input row count
- no keyword is blank unless the source row was blank and preserved
- metrics were not overwritten
- every generated ID is unique
- near-match rows are grouped but not removed
- risky and off-topic words are preserved with labels
