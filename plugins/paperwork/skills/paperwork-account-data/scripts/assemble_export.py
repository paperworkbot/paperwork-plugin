"""Assemble locally saved data_export pages; standard library, no network or auth."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys


class InvalidExport(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidExport(message)


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value):
    raise InvalidExport("non-finite JSON number")


def decode(text):
    try:
        return json.loads(text, object_pairs_hook=object_pairs,
                          parse_constant=reject_constant)
    except (ValueError, RecursionError) as error:
        # Parser errors may quote private input; expose only a fixed diagnostic.
        raise InvalidExport("invalid JSON or duplicate keys") from error


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def read_page(path, remaining):
    require(remaining > 0, "saved input byte budget exceeded")
    flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW
    with os.fdopen(os.open(path, flags), "rb") as source:
        require(stat.S_ISREG(os.fstat(source.fileno()).st_mode),
                "saved page must be a regular local file")
        raw = source.read(remaining + 1)
    require(len(raw) <= remaining, "saved input byte budget exceeded")
    try:
        page = decode(raw.decode("utf-8"))
    except UnicodeError as error:
        raise InvalidExport("saved page must be UTF-8") from error
    require(isinstance(page, dict) and set(page) == {"request", "response"},
            "save each page as a request/response object")
    return page, len(raw)


def nonempty_string(value):
    return isinstance(value, str) and bool(value)


def cursor_value(value):
    return value is None or nonempty_string(value)


def validate_request(request):
    require(isinstance(request, dict), "request must be an object")
    require(set(request) <= {"relation", "fields", "filters", "limit", "cursor"},
            "unsupported export request argument")
    require(nonempty_string(request.get("relation")), "request needs a relation")
    if "fields" in request:
        validate_fields(request["fields"])
    if "limit" in request:
        require(type(request["limit"]) is int and 1 <= request["limit"] <= 200,
                "request limit must be 1..200")
    filters = request.get("filters", [])
    require(isinstance(filters, list), "filters must be an array")
    for item in filters:
        require(isinstance(item, dict) and nonempty_string(item.get("field"))
                and nonempty_string(item.get("op")), "filters need field and op")
        expected_keys = {"field", "op"} if item["op"] == "present" else {"field", "op", "value"}
        require(set(item) == expected_keys, "filter value must match operator requirements")
        value = item.get("value")
        values = value if isinstance(value, list) else [value]
        require(all(type(element) in (str, int, bool, type(None)) for element in values),
                "filter values must be strings, integers, booleans, null, or arrays of these")
    require(cursor_value(request.get("cursor")), "invalid request cursor")
    return {key: value for key, value in request.items() if key != "cursor"}


def validate_fields(fields):
    require(isinstance(fields, list) and fields
            and all(nonempty_string(field) for field in fields)
            and len(set(fields)) == len(fields), "fields must be unique names")


def query_fingerprint(schema_version, relation, fields, filters):
    # Matches Ruby JSON.generate for the supported scalar/array filter values.
    # Preserve filter and array order; the valueless present operator hashes null.
    normalized_filters = [[item["field"], item["op"], item.get("value")] for item in filters]
    return hashlib.sha256(encoded([schema_version, relation, fields, normalized_filters])).hexdigest()


def assemble(paths, output_dir, *, allow_incomplete=False,
             max_input_bytes=64 * 1024 * 1024, max_data_bytes=32 * 1024 * 1024,
             max_pages=1000):
    """Validate all pages before creating a new private output directory."""
    require(paths and 1 <= len(paths) <= max_pages, "saved page budget exceeded or empty")
    require(max_input_bytes > 0 and max_data_bytes > 0, "byte budgets must be positive")
    chunks, receipts = [], []
    input_bytes = data_bytes = row_count = 0
    expected_cursor = None
    seen_cursors = set()
    base_query = base_identity = base_fingerprints = None
    final_coverage = None

    for number, path in enumerate(paths, 1):
        page, size = read_page(path, max_input_bytes - input_bytes)
        input_bytes += size
        request, response = page["request"], page["response"]
        query = validate_request(request)
        require(request.get("cursor") == expected_cursor,
                "cursor chain must start at null and be contiguous")
        require(isinstance(response, dict), "response must be an object")
        require("cursor" in response and response["cursor"] == request.get("cursor"),
                "response cursor is required and must match request cursor")
        require(response.get("schema_version") == "1", "unsupported response schema version")
        fields = response.get("fields")
        validate_fields(fields)
        require(response.get("relation") == request["relation"], "relation mismatch")
        if "fields" in request:
            require(fields == request["fields"], "requested fields mismatch")
        identity = {key: response[key] for key in ("schema_version", "relation", "fields")}
        manifest = response.get("manifest")
        require(isinstance(manifest, dict), "export response needs a manifest")
        for key, value in identity.items():
            require(manifest.get(key) == value, "manifest identity mismatch")
        require(manifest.get("format") == "jsonl" and manifest.get("consistency") == "live"
                and nonempty_string(manifest.get("generated_at")), "invalid export manifest")
        if "format" in response:
            require(response["format"] == "jsonl", "export format must be jsonl")
        fingerprints = {key: value for key, value in manifest.items()
                        if key.endswith("_fingerprint")}
        require({"scope_fingerprint", "query_fingerprint"} <= set(fingerprints)
                and all(nonempty_string(value) for value in fingerprints.values()),
                "manifest fingerprints must be nonempty strings")
        require(manifest["query_fingerprint"] == query_fingerprint(
                    response["schema_version"], request["relation"], fields, request.get("filters", [])),
                "manifest query_fingerprint does not match saved request")
        if base_query is None:
            base_query, base_identity, base_fingerprints = query, identity, fingerprints
        else:
            require(encoded(query) == encoded(base_query), "export query changed between pages")
            require(identity == base_identity, "export schema or fields changed between pages")
            require(fingerprints == base_fingerprints,
                    "manifest fingerprints changed or disappeared between pages")

        require("next_cursor" in response and cursor_value(response["next_cursor"]),
                "response needs a valid next_cursor")
        next_cursor = response["next_cursor"]
        require(type(response.get("has_more")) is bool
                and response["has_more"] == (next_cursor is not None),
                "has_more and next_cursor disagree")
        require(next_cursor is None or next_cursor not in seen_cursors, "replayed cursor")
        if next_cursor is not None:
            seen_cursors.add(next_cursor)
        coverage = response.get("coverage")
        require(isinstance(coverage, dict) and type(coverage.get("complete")) is bool
                and coverage.get("consistency") == "live", "invalid live coverage")
        require(not coverage["complete"] or next_cursor is None,
                "complete coverage cannot have a continuation")

        data = response.get("data")
        require(isinstance(data, str), "export needs a JSONL data string")
        try:
            payload = data.encode("utf-8")
        except UnicodeError as error:
            raise InvalidExport("JSONL must be UTF-8") from error
        source_sha256 = hashlib.sha256(payload).hexdigest()
        require(manifest.get("page_sha256") == source_sha256, "page checksum mismatch")
        require(type(manifest.get("byte_count")) is int and manifest["byte_count"] == len(payload),
                "manifest byte_count mismatch")
        if payload and not payload.endswith(b"\n"):
            payload += b"\n"
        data_bytes += len(payload)
        require(data_bytes <= max_data_bytes, "JSONL data byte budget exceeded")
        lines = payload.splitlines()
        for line in lines:
            row = decode(line)
            require(isinstance(row, dict) and set(row) == set(fields),
                    "JSONL rows must have exactly the selected fields")
        returned = response.get("returned_rows")
        require(type(returned) is int and returned == len(lines)
                and 0 <= returned <= request.get("limit", 200), "returned_rows mismatch")
        require(type(manifest.get("row_count")) is int and manifest["row_count"] == returned,
                "manifest row_count mismatch")
        # An empty page can still advance the cursor. Never stop on its row count.
        row_count += returned
        chunks.append(payload)
        receipts.append({"page": number, "returned_rows": returned,
                         "sha256": hashlib.sha256(payload).hexdigest(),
                         "source_page_sha256": source_sha256,
                         "generated_at": manifest["generated_at"], "coverage": coverage})
        expected_cursor, final_coverage = next_cursor, coverage
        require(number == len(paths) or next_cursor is not None,
                "unexpected page after terminal cursor")

    complete = expected_cursor is None and final_coverage["complete"]
    require(complete or allow_incomplete,
            "incomplete export; save remaining pages or use --allow-incomplete")
    data = b"".join(chunks)
    result = {
        "assembly_schema_version": "1", **base_identity,
        "query": base_query, "query_sha256": hashlib.sha256(encoded(base_query)).hexdigest(),
        "fingerprints": base_fingerprints,
        "scope_verification": "server_fingerprint",
        "file": "data.jsonl", "sha256": hashlib.sha256(data).hexdigest(),
        "data_bytes": len(data), "input_bytes": input_bytes, "returned_rows": row_count,
        "page_count": len(paths), "next_cursor": expected_cursor,
        "coverage": {"complete": complete, "consistency": "live",
                     "point_in_time": False, "reason": "cursor_exhausted" if complete else "incomplete"},
        "pages": receipts,
    }
    write_private_output(output_dir, data, encoded(result) + b"\n")
    return result


def write_private_output(output_dir, data, manifest):
    # Exclusive directory creation also refuses existing paths and symlinks.
    destination = Path(output_dir)
    os.mkdir(destination, mode=0o700)
    created = []
    try:
        for name, contents in (("data.jsonl", data), ("manifest.json", manifest)):
            path = destination / name
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            created.append(path)
            with os.fdopen(descriptor, "wb") as target:
                target.write(contents)
    except BaseException:
        for path in created:
            path.unlink()
        destination.rmdir()
        raise


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", nargs="+", help="saved request/response JSON files, in cursor order")
    parser.add_argument("--output-dir", required=True, help="new private directory; parent must exist")
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument("--max-input-bytes", type=positive, default=64 * 1024 * 1024)
    parser.add_argument("--max-data-bytes", type=positive, default=32 * 1024 * 1024)
    parser.add_argument("--max-pages", type=positive, default=1000)
    args = parser.parse_args()
    try:
        result = assemble(args.pages, args.output_dir, allow_incomplete=args.allow_incomplete,
                          max_input_bytes=args.max_input_bytes, max_data_bytes=args.max_data_bytes,
                          max_pages=args.max_pages)
    except InvalidExport as error:
        print("Export rejected: " + str(error), file=sys.stderr)
        return 1
    except (OSError, UnicodeError, ValueError, RecursionError):
        print("Export failed: check local files, new output directory, and permissions.", file=sys.stderr)
        return 1
    print(json.dumps({key: result[key] for key in ("returned_rows", "page_count", "sha256", "coverage")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
