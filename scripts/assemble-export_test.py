"""Synthetic, offline regression tests for saved account-data exports."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = (Path(__file__).resolve().parents[1] / "plugins/paperwork/skills/"
          "paperwork-account-data/scripts/assemble_export.py")
SPEC = importlib.util.spec_from_file_location("assemble_export", SCRIPT)
export = importlib.util.module_from_spec(SPEC)
sys.dont_write_bytecode = True
SPEC.loader.exec_module(export)


def page(cursor=None, next_cursor=None, rows=None, filters=None):
    rows = [{"reference": "EXT-731", "label": "Café sample"}] if rows is None else rows
    filters = [] if filters is None else filters
    fields = ["reference", "label"]
    data = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    query_bytes = json.dumps(["1", "items", fields,
                             [[item["field"], item["op"], item.get("value")] for item in filters]],
                            ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "request": {"relation": "items", "fields": fields, "filters": filters,
                    "limit": 200, "cursor": cursor},
        "response": {
            "schema_version": "1", "relation": "items", "fields": fields,
            "data": data, "returned_rows": len(rows), "cursor": cursor, "next_cursor": next_cursor,
            "has_more": next_cursor is not None,
            "coverage": {"complete": next_cursor is None, "consistency": "live"},
            "manifest": {
                "format": "jsonl", "schema_version": "1", "relation": "items", "fields": fields,
                "scope_fingerprint": hashlib.sha256(b"synthetic-scope").hexdigest(),
                "query_fingerprint": hashlib.sha256(query_bytes).hexdigest(),
                "page_sha256": hashlib.sha256(data.encode()).hexdigest(),
                "row_count": len(rows), "byte_count": len(data.encode()),
                "generated_at": "2026-01-01T00:00:00Z", "consistency": "live",
            },
        },
    }


def refresh_data_receipt(saved):
    response = saved["response"]
    raw = response["data"].encode()
    response["manifest"]["page_sha256"] = hashlib.sha256(raw).hexdigest()
    response["manifest"]["byte_count"] = len(raw)


class AssembleExportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="paperwork-export-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "assembled"

    def save(self, pages):
        paths = []
        for index, value in enumerate(pages):
            path = self.root / f"page-{index}.json"
            path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
            paths.append(path)
        return paths

    def assemble(self, pages, **kwargs):
        return export.assemble(self.save(pages), self.output, **kwargs)

    def rejected(self, pages, **kwargs):
        with self.assertRaises(export.InvalidExport):
            self.assemble(pages, **kwargs)
        self.assertFalse(self.output.exists())

    def test_contiguous_export_including_empty_continuation_is_private_and_reproducible(self):
        pages = [page(next_cursor="cursor-a"), page("cursor-a", "cursor-b", []),
                 page("cursor-b", rows=[{"reference": "EXT-984", "label": "Second sample"}])]
        paths = self.save(pages)
        # Assembly never needs a network socket, even if a source field contains a URL.
        with patch.object(socket, "socket", side_effect=AssertionError("network access")):
            result = export.assemble(paths, self.output)
        data = (self.output / "data.jsonl").read_bytes()
        self.assertEqual([json.loads(line) for line in data.splitlines()],
                         [json.loads(pages[0]["response"]["data"]),
                          json.loads(pages[2]["response"]["data"])])
        self.assertEqual(result["returned_rows"], 2)
        self.assertEqual(result["page_count"], 3)
        self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(result["coverage"], {"complete": True, "consistency": "live",
                                            "point_in_time": False, "reason": "cursor_exhausted"})
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        for name in ("data.jsonl", "manifest.json"):
            self.assertEqual((self.output / name).stat().st_mode & 0o777, 0o600)
        replay = self.root / "replay"
        self.assertEqual(export.assemble(paths, replay), result)
        self.assertEqual((replay / "data.jsonl").read_bytes(), data)

    def test_empty_terminal_dataset_and_omitted_defaults(self):
        saved = page(rows=[])
        saved["request"] = {"relation": "items"}
        result = self.assemble([saved])
        self.assertEqual(result["returned_rows"], 0)
        self.assertTrue(result["coverage"]["complete"])

    def test_present_operator_has_no_value_and_cursor_echo_must_match(self):
        saved = page(filters=[{"field": "label", "op": "present"}])
        self.assertTrue(self.assemble([saved])["coverage"]["complete"])
        other = self.root / "other"
        saved["response"]["cursor"] = "wrong-cursor"
        with self.assertRaises(export.InvalidExport):
            export.assemble(self.save([saved]), other)
        saved["response"]["cursor"] = None
        saved["request"]["filters"][0]["value"] = True
        with self.assertRaises(export.InvalidExport):
            export.assemble(self.save([saved]), other)
        self.assertFalse(other.exists())

    def test_cursor_echo_is_required_on_first_and_later_pages(self):
        saved = page()
        del saved["response"]["cursor"]
        self.rejected([saved])
        first, second = page(next_cursor="cursor-a"), page("cursor-a")
        del second["response"]["cursor"]
        self.rejected([first, second])

    def test_terminal_suffix_cannot_be_relabeled_as_a_complete_first_page(self):
        saved = page(cursor="cursor-a")
        saved["request"]["cursor"] = None
        self.rejected([saved])
        del saved["response"]["cursor"]
        self.rejected([saved])

    def test_intact_unfiltered_page_cannot_be_relabeled_as_filtered(self):
        saved = page()
        saved["request"]["filters"] = [{"field": "state", "op": "eq", "value": "completed"}]
        with self.assertRaisesRegex(export.InvalidExport, "query_fingerprint does not match saved request"):
            self.assemble([saved])
        self.assertFalse(self.output.exists())

    def test_query_hash_matches_ruby_for_unicode_boolean_null_integer_array_and_present(self):
        filters = [
            {"field": "label", "op": "eq", "value": 'Café 雪 🧾\n"sample"\\'},
            {"field": "enabled", "op": "eq", "value": True},
            {"field": "archived", "op": "eq", "value": False},
            {"field": "optional", "op": "eq", "value": None},
            {"field": "quantity", "op": "in", "value": [0, -7, 12345678901234567890]},
            {"field": "label", "op": "in", "value": ["é", "雪", None]},
            {"field": "reference", "op": "present"},
        ]
        saved = page(filters=filters)
        # Independent vector generated with Ruby JSON.generate + Digest::SHA256.
        ruby_digest = "647b610450dd3278aaa88cea43cd1e57fe634387d9baae8d94c4e703cc329c40"
        saved["response"]["manifest"]["query_fingerprint"] = ruby_digest
        result = self.assemble([saved])
        self.assertEqual(result["fingerprints"]["query_fingerprint"], ruby_digest)

    def test_default_projection_uses_response_fields_for_server_query_hash(self):
        saved = page()
        saved["request"] = {"relation": "items"}
        saved["response"]["manifest"]["query_fingerprint"] = (
            "31b19aa7909f48365512b0bad998d178daaf9e1007deb46dac1368bceb293f4c")
        result = self.assemble([saved])
        self.assertEqual(result["fields"], ["reference", "label"])
        self.assertTrue(result["coverage"]["complete"])

    def test_query_hash_preserves_filter_order_array_order_and_values(self):
        def filtered_page():
            return page(filters=[{"field": "label", "op": "in", "value": ["A", "B"]},
                                 {"field": "enabled", "op": "eq", "value": True}])

        reordered_filters = filtered_page()
        reordered_filters["request"]["filters"].reverse()
        reordered_values = filtered_page()
        reordered_values["request"]["filters"][0]["value"].reverse()
        changed_value = filtered_page()
        changed_value["request"]["filters"][1]["value"] = 1
        for saved in (reordered_filters, reordered_values, changed_value):
            with self.assertRaisesRegex(export.InvalidExport, "query_fingerprint does not match saved request"):
                self.assemble([saved])
            self.assertFalse(self.output.exists())

    def test_query_hash_rejects_unsupported_numeric_and_object_values(self):
        for value in (1.5, {"nested": "value"}, [["nested"]]):
            with self.subTest(value=value):
                self.rejected([page(filters=[{"field": "label", "op": "eq", "value": value}])])

    def test_missing_final_newline_is_verified_then_normalized(self):
        saved = page()
        saved["response"]["data"] = saved["response"]["data"].rstrip("\n")
        refresh_data_receipt(saved)
        result = self.assemble([saved])
        self.assertTrue((self.output / "data.jsonl").read_bytes().endswith(b"\n"))
        self.assertNotEqual(result["pages"][0]["sha256"], result["pages"][0]["source_page_sha256"])

    def test_incomplete_prefix_requires_opt_in_and_preserves_cursor(self):
        saved = page(next_cursor="cursor-a")
        self.rejected([saved])
        result = self.assemble([saved], allow_incomplete=True)
        self.assertFalse(result["coverage"]["complete"])
        self.assertEqual(result["next_cursor"], "cursor-a")

    def test_terminal_incomplete_coverage_is_not_promoted(self):
        saved = page()
        saved["response"]["coverage"]["complete"] = False
        self.rejected([saved])
        result = self.assemble([saved], allow_incomplete=True)
        self.assertFalse(result["coverage"]["complete"])

    def test_cursor_gaps_replays_cycles_and_pages_after_terminal_are_rejected(self):
        variants = [
            [page(cursor="cursor-a")],
            [page(next_cursor="cursor-a"), page(cursor="cursor-b")],
            [page(next_cursor="cursor-a"), page(next_cursor="cursor-a")],
            [page(next_cursor="cursor-a"), page("cursor-a", "cursor-a")],
            [page(), page()],
            [page(next_cursor="cursor-a"), page("cursor-a", "cursor-b"), page("cursor-b", "cursor-a")],
        ]
        for pages in variants:
            with self.subTest(pages=variants.index(pages)):
                self.rejected(pages, allow_incomplete=True)

    def test_changed_query_scope_schema_or_missing_fingerprint_is_rejected(self):
        paths = [
            ("request", "filters", [{"field": "label", "op": "eq", "value": "Sample"}]),
            ("request", "limit", 20),
            ("response", "schema_version", "2"),
            ("response", "fields", ["label", "reference"]),
            ("manifest", "scope_fingerprint", "different-synthetic-scope"),
            ("manifest", "query_fingerprint", "different-synthetic-query"),
            ("manifest", "schema_version", "2"),
        ]
        for section, key, value in paths:
            with self.subTest(section=section, key=key):
                first, second = page(next_cursor="cursor-a"), page("cursor-a")
                target = second["response"]["manifest"] if section == "manifest" else second[section]
                target[key] = value
                self.rejected([first, second])
        for key in ("scope_fingerprint", "query_fingerprint"):
            first, second = page(next_cursor="cursor-a"), page("cursor-a")
            del second["response"]["manifest"][key]
            self.rejected([first, second])

    def test_invalid_paging_and_coverage_metadata_is_rejected(self):
        for key, value in [("has_more", True), ("has_more", 0), ("next_cursor", ""),
                           ("returned_rows", True), ("returned_rows", 2),
                           ("coverage", {"complete": True, "consistency": "snapshot"}),
                           ("manifest", None)]:
            with self.subTest(key=key, value=value):
                saved = page()
                saved["response"][key] = value
                self.rejected([saved])
        saved = page(next_cursor="cursor-a")
        saved["response"]["coverage"]["complete"] = True
        self.rejected([saved], allow_incomplete=True)
        saved = page()
        del saved["response"]["next_cursor"]
        self.rejected([saved])

    def test_page_checksum_and_counts_are_verified(self):
        for key, value in [("page_sha256", "bad-digest"), ("byte_count", 1),
                           ("row_count", 0), ("row_count", True), ("byte_count", True)]:
            with self.subTest(key=key):
                saved = page()
                saved["response"]["manifest"][key] = value
                self.rejected([saved])

    def test_malformed_jsonl_blank_rows_duplicate_keys_and_unselected_fields_fail(self):
        for data in ['{', '\n', '[]\n', '{"reference":"EXT-883"}\n',
                     '{"reference":"a","reference":"b","label":"sample"}\n',
                     '{"reference":"a","label":NaN}\n',
                     '{"reference":"a","label":"sample","extra":1}\n']:
            with self.subTest(data=data):
                saved = page()
                saved["response"]["data"] = data
                refresh_data_receipt(saved)
                self.rejected([saved])

    def test_size_and_page_budgets_fail_before_output_even_with_partial_opt_in(self):
        for options in [{"max_input_bytes": 10}, {"max_data_bytes": 1}, {"max_pages": 0}]:
            with self.subTest(options=options):
                self.rejected([page()], allow_incomplete=True, **options)
        paths = self.save([page(next_cursor="cursor-a"), page("cursor-a")])
        with self.assertRaises(export.InvalidExport):
            export.assemble(paths, self.output, max_input_bytes=paths[0].stat().st_size + 1)
        self.assertFalse(self.output.exists())

    def test_existing_destination_and_symlinks_are_never_overwritten(self):
        paths = self.save([page()])
        self.output.mkdir()
        sentinel = self.output / "data.jsonl"
        sentinel.write_text("keep me")
        with self.assertRaises(FileExistsError):
            export.assemble(paths, self.output)
        self.assertEqual(sentinel.read_text(), "keep me")
        link = self.root / "output-link"
        link.symlink_to(self.output, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            export.assemble(paths, link)
        source_link = self.root / "page-link"
        source_link.symlink_to(paths[0])
        with self.assertRaises(OSError):
            export.assemble([source_link], self.root / "unused")
        self.assertFalse((self.root / "unused").exists())

    def test_special_files_are_rejected_without_blocking(self):
        fifo = self.root / "page-fifo"
        os.mkfifo(fifo)
        with self.assertRaises(export.InvalidExport):
            export.assemble([fifo], self.output)
        self.assertFalse(self.output.exists())

    def test_cli_rejects_malformed_envelope_without_echoing_private_input(self):
        bad = self.root / "bad.json"
        bad.write_text('{"sensitive-example": this is invalid}')
        run = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(self.output), str(bad)],
                             capture_output=True, text=True, timeout=5)
        self.assertEqual(run.returncode, 1)
        self.assertNotIn("sensitive-example", run.stderr)
        self.assertFalse(self.output.exists())

    def test_malformed_envelope_and_invalid_arguments_fail_before_output(self):
        self.rejected([{"response": page()["response"]}])
        for key, value in [("limit", 201), ("limit", True), ("filters", "not-an-array"),
                           ("fields", ["reference", "reference"]), ("cursor", []),
                           ("url", "https://account.example.com/export")]:
            with self.subTest(key=key):
                saved = page()
                saved["request"][key] = value
                self.rejected([saved])

    def test_cli_success_prints_summary_without_rows_or_cursors(self):
        paths = self.save([page(next_cursor="cursor-a")])
        run = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(self.output),
                              "--allow-incomplete", str(paths[0])],
                             capture_output=True, text=True, timeout=5)
        self.assertEqual(run.returncode, 0, run.stderr)
        summary = json.loads(run.stdout)
        self.assertFalse(summary["coverage"]["complete"])
        self.assertNotIn("cursor-a", run.stdout)
        self.assertNotIn("EXT-731", run.stdout)


if __name__ == "__main__":
    unittest.main()
