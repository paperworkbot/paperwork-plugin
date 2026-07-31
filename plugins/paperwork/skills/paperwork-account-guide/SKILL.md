---
name: paperwork-account-guide
description: Discover a Paperwork account's authorized vocabulary over MCP. Use before filtering by paperwork type, state, resolution, role, agent, queue, or download variant, or when the user asks what their account and agents support. Read-only.
---

# Paperwork Account Guide

Call `account_describe` once before work that depends on account-specific keys.
Do not guess keys from display labels or examples.

## Procedure

1. Call `account_describe`.
2. Use the returned values as the source of truth for:
   - standard and custom paperwork type keys;
   - workflow, task, and document states;
   - document and workflow resolutions;
   - account roles and task queues;
   - visible agents, their keys, and their contact roles; and
   - supported download variants.
3. Select only values needed by the user's request. Preserve machine keys in
   tool arguments and use display labels in the explanation.
4. If the requested type, agent, role, state, or variant is unavailable, say
   so and offer the nearest valid choices. Do not silently substitute one.

## Output

For a general account overview, summarize:

- available workflow agents and what each appears to handle;
- standard and custom paperwork types;
- roles and queues the user can work;
- lifecycle states and resolutions; and
- available download representations.

For an operational request, keep the account description as working context
and continue into the focused Paperwork skill without dumping the full catalog.

## Rules

- Read-only. Never change account or agent configuration.
- The result reflects the acting user's current authorization. Do not
  speculate about hidden agents, roles, or types.
- Refresh when a later tool rejects a previously valid key or the user says
  account configuration changed.

See [the capability map](../paperwork/references/capabilities.yml) when
diagnosing a missing grant.
