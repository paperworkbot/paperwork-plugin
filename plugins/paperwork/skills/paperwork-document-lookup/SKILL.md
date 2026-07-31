---
name: paperwork-document-lookup
description: Check whether one or many business document identifiers already exist in Paperwork and how far each has progressed. Use for duplicate checks, invoice or statement reconciliation, prior-seen questions, batch identifier checks, and existence verification before intake or action. Read-only.
---

# Paperwork Document Lookup

Answer whether the identifiers exist and distinguish exact evidence from
approximate matches.

## Procedure

1. If the paperwork type key is unknown, call `account_describe` and use an
   exact standard or custom type key.
2. Preserve identifiers verbatim, including punctuation, spacing, and leading
   zeros.
3. Call `paperworks_find_by_identifier` with:
   - `paperwork_type`;
   - one `identifier`, or `identifiers` containing up to 25 values;
   - an optional `identifier_kind`; and
   - account scope unless the user explicitly asks for agent scope.
4. Interpret each `reconciliation_status_hint`:
   - `missing`: no authorized match;
   - `matched`: one credible match;
   - `on_hold`: a match whose workflow needs attention;
   - `duplicate`: multiple candidates that must remain distinct.
5. Inspect `match_kind`. Treat zero-padding, affix trimming, prefix, and other
   approximate matches as probable, never definitive.
6. For more detail:
   - `paperworks_get` for each selected document dossier;
   - `processes_history` for why a workflow is held or unresolved; or
   - `paperworks_search` as a bounded fallback when an identifier may have been
     extracted differently.

## Output

For one identifier, lead with a direct yes/no/probable answer. For batches,
return a compact table with:

- queried identifier;
- reconciliation hint;
- matched paperwork and workflow references;
- states and resolution; and
- match kind or ambiguity.

List every duplicate candidate. Never silently select one.

## Rules

- Read-only. Never create, close, mark duplicate, or reprocess paperwork.
- "Missing" means no authorized match was returned; do not imply global
  nonexistence outside the user's view.
- An approximate match is evidence for review, not proof.
- Route requested document changes to
  [paperwork-document-management](../paperwork-document-management/SKILL.md).
