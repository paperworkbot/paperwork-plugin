---
name: paperwork-document-lookup
description: Check whether a document already exists in Paperwork and how far it has progressed, over the Paperwork MCP connection. Use when the user asks "does <identifier> exist", "have we seen this document", "was this already processed", "is this a duplicate", or before entering or acting on a document. Read-only.
---

# Document Lookup

Answer "have we seen this before, and where does it stand?" — the question
behind duplicate checks, reconciliation, and reviewing a document reference
someone sent in. Works for any document type Paperwork tracks; the identifier
is whatever business reference the document carries.

Requires the Paperwork MCP server (tools named like
`paperworks_find_by_identifier`).

## Procedure

1. Call `paperworks_find_by_identifier` with:
   - `paperwork_type` — the kind of document the user is checking.
   - `identifier` — **verbatim, punctuation and all**, exactly as it appears
     on the document. The matcher handles separator, spacing, and zero-padding
     differences itself.
2. Interpret the result by its `reconciliation_status_hint`:
   - **`missing`** — no record. Safe to treat as new. Offer a fallback
     `paperworks_search` on a fragment in case the identifier was extracted
     differently.
   - **`matched`** — one match. Report the paperwork reference, its state and
     resolution, and the owning workflow's reference and state.
   - **`on_hold`** — it exists but its workflow is on hold. Say why it might
     be stuck and offer `processes_history` on that workflow.
   - **`duplicate`** — multiple candidates. List every candidate with its
     workflow; warn about the risk of acting on the same document twice; never
     silently pick one.
3. Check `match_kind` on each match. Anything flagged approximate
   (zero-padding, trimmed affixes, long-prefix) is a **probable** match, not a
   confirmation — say so explicitly, and show the matched key so the user can
   judge.
4. When the user wants detail on a match, `context_get` and
   `processes_history` on its workflow tell the rest of the story.

## Output

One direct sentence first — "yes, that identifier exists as PW-187 on workflow
WF-202, closed as processed" or "no record of that identifier" — then the
supporting detail. For duplicates, a short candidate table with references,
states, and match kinds.

## Rules

- Read-only. This skill never creates, closes, or reprocesses anything.
- Preserve the user's identifier exactly in the lookup; show both the queried
  and the matched form when they differ.
- An approximate match is evidence, not proof. Do not tell the user a document
  "definitely exists" on an approximate match kind.
