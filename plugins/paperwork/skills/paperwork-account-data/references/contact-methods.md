# Contact-method analysis

Discover `contact_methods` through the existing `data_describe`, then use
`data_scan` or separately granted `data_export`. No new capability is needed.
Each row requires an account-scoped, readable parent contact. Task-only users
cannot discover this relation; workflow scope is unsupported. A denied or
missing relation is not permission to bypass that boundary.

## Fields and local join

All fields are typed strings; absent or inapplicable values are null, never
nested objects or arrays. The default projection is `reference`,
`contact_reference`, `method_type`, and `label`.

| Fields | Meaning |
| --- | --- |
| `reference` | Contact-method UUID; identifies the method, not its parent |
| `contact_reference` | Join to `contacts.reference` locally |
| `method_type`, `label` | Method kind and descriptive label |
| `email` | Populated only for `email` methods |
| `phone` | Populated only for `phone` methods |
| `username` | Populated only for `social_media` methods |
| `address_line_1`, `address_line_2`, `city`, `state`, `postal_code`, `country_code`, `addressee` | Populated only for `address` methods |

Select the needed business fields explicitly; defaults omit method values.
Join separately retrieved contacts and methods on
`contact_methods.contact_reference = contacts.reference`. Expect multiple
methods per contact. Count distinct parent references for observed contacts
and method UUIDs for methods; do not join by label, email, or method UUID.
Check duplicate join keys and retain unmatched methods as unresolved. Filters,
permissions, bounded coverage, and changes between live reads can explain
missing matches; they do not prove that a parent or method does not exist.

## Filters and address quality

Use live-discovered operators. For example, an address scan can select
`reference`, `contact_reference`, `method_type`, `label`, `address_line_1`,
`city`, `state`, `postal_code`, and `country_code` with these ANDed filters:

```json
[
  {"field": "method_type", "op": "eq", "value": "address"},
  {"field": "country_code", "op": "eq", "value": "US"}
]
```

For a known contact cohort, add a bounded `contact_reference` `in` filter using
references actually returned by the authorized contacts query. An additional
`postal_code` `eq` filter with `value: null` selects nulls only; `present` takes
no value and tests non-null, not nonblank. To include empty or whitespace-only
strings, collect the bounded address cohort and check trimmed strings locally.
Preserve postal codes and phone numbers as strings, including leading zeros.

Evaluate only address rows for address quality. Null address fields on email,
phone, or social-media methods are expected. Report missing or blank values
under an explicit rule appropriate to the country or user's question; optional
address fields are not universally required. Multiple addresses and labels
such as `main` do not identify an authoritative main address. Findings are
review candidates, not permission to edit contacts or write back from a dataset.

There are no `created_at`, `updated_at`, or `record_version` fields: this
relation has no model timestamps and cannot support incremental timestamp sync.
Export manifest `generated_at` dates the export, not the method's last change.
Even terminal coverage is a live traversal of the permitted selection, not an
all-contacts snapshot or proof that every contact or method is visible. Report
each relation's filters, budget, row counts, and coverage alongside join results.
