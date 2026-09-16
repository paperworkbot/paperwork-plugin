# Saved export pages

The tool harness performs `data_export` using the existing MCP connection. Save
one UTF-8 JSON file per response, in request order, with exactly two top-level
keys: `request` (the exact tool arguments) and `response` (the decoded result
object, not the MCP content-block wrapper). Omitted initial cursor means null.
Preserve all other arguments across the chain, including omitted defaults.
The `present` filter takes `{field, op: 'present'}` without a `value`; other
operators take `{field, op, value}`. Every response must contain a `cursor` echo
exactly matching the request cursor, including null on the first page. A missing
echo is rejected; a terminal suffix cannot stand in for a full traversal.

Structural example only; relation and field names must come from live discovery:

```json
{
  "request": {"relation": "items", "fields": ["reference"], "limit": 200},
  "response": {
    "schema_version": "1",
    "relation": "items",
    "fields": ["reference"],
    "data": "",
    "returned_rows": 0,
    "cursor": null,
    "next_cursor": null,
    "has_more": false,
    "coverage": {"complete": true, "consistency": "live"},
    "manifest": {
      "format": "jsonl",
      "schema_version": "1",
      "relation": "items",
      "fields": ["reference"],
      "scope_fingerprint": "synthetic-scope",
      "query_fingerprint": "0de51112a60d1d6a3872fed6e9352cc789cbbb518b4f62d71b4a001cea17de20",
      "page_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "row_count": 0,
      "byte_count": 0,
      "generated_at": "2026-01-01T00:00:00Z",
      "consistency": "live"
    }
  }
}
```

The manifest's `scope_fingerprint` binds account, user, connection, capability
grants, and workflow binding without raw account metadata. `query_fingerprint`
binds relation, fields, and filters. Require both fingerprints and identical
schema metadata on every page, including empty pages. Other manifest keys ending
in `_fingerprint` must also remain present and equal if supplied. The helper
compares opaque scope values; it cannot reconstruct or authenticate server scope.

It also recomputes `query_fingerprint` for every saved request as SHA-256 of the
UTF-8 JSON array `["1", relation, resolved_fields, normalized_filters]`, matching
the server's Ruby `JSON.generate`. `resolved_fields` are the response's selected
fields (which must match explicit request fields, or resolve omitted defaults).
Each normalized filter is `[field, op, value]`, with null for the valueless
`present` operator. Filter order, array order, and values are preserved. JSON is
compact with unescaped Unicode (`ensure_ascii=False`, `separators=(",", ":")` in
Python); supported values are strings, integers, booleans, null, and arrays of
these. Limits and cursors are not part of this server query digest. This rejects
an intact unfiltered page whose envelope was relabeled with different filters.
The local manifest's `query_sha256` separately hashes the saved query object.

`page_sha256` hashes the exact UTF-8 bytes of `data`; `byte_count` and `row_count`
must match. Export pages contain whole JSONL objects, not split JSON fragments.
The server bounds payloads around 256 KiB and never silently truncates records;
an error is not an empty or complete result. The helper requires each row to
contain exactly the selected fields, with null values represented explicitly.

## Assemble

From this skill directory, with saved pages in a private local working directory:

```sh
python3 scripts/assemble_export.py \
  --output-dir /tmp/private-analysis/export-001 \
  /tmp/private-analysis/page-001.json /tmp/private-analysis/page-002.json
```

Use the actual private workspace path; the example parent must already exist
with private permissions. Pass explicit filenames in cursor order. Inputs must
be regular local files, not symlinks, pipes, devices, URLs, or credential files.
The helper has no network/authentication functionality and does not inspect
environment variables or credential stores. Do not pass those files as input.

The helper validates every input before creating output. Defaults bound total
saved input to 64 MiB, JSONL output to 32 MiB, and pages to 1,000. Flags
`--max-input-bytes`, `--max-data-bytes`, and `--max-pages` set explicit bounds;
these do not increase the retrieval budget agreed with the user. Exceeding any
helper limit fails without output; split analysis into explicitly scoped queries
or choose a justified bound before rerunning.

Output uses a new directory (mode 0700), with `data.jsonl` and `manifest.json`
(mode 0600). Existing destinations, including symlinks, are refused. There is no
overwrite option. A missing final newline is normalized on each page so adjacent
records cannot fuse; page source checksums and the assembled checksum are recorded
separately. The assembled manifest includes the query, opaque scope/query
fingerprints, row/page/byte counts, page receipts, SHA-256, continuation cursor,
and explicit live coverage. Filenames and raw input paths are not copied into it.

## Partial traversal and replay

A chain must begin at null and each subsequent request cursor must equal the
preceding response's `next_cursor`. Gaps, changed queries, repeated cursors,
replayed pages, and pages after terminal continuation are errors. Never stop just
because `data` is empty: that page may advance through rows outside visibility.

If saved pages end before `coverage.complete: true` and null `next_cursor`, the
default invocation refuses assembly. `--allow-incomplete` permits analysis of the
available prefix and sets `coverage.complete: false` with the last continuation
cursor. Preserve that status in every analysis; do not describe sample totals as
account totals. To resume, fetch the next page through MCP with the same query,
then assemble the entire chain into a different output directory. If authorization
or fingerprints changed, begin a separate traversal; never splice scopes.

Even a complete chain is a live traversal. Rows can change between calls and
cross-relation joins have no snapshot guarantee. Checksum-valid saved pages can
be reassembled locally without making another server call; they do not prove
current authorization, completeness of hidden data, or server authenticity.
