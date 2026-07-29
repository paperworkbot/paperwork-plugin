# Paperwork Plugin

One plugin that connects your coding agent — Claude Code or Codex — to your
Paperwork account and teaches it to work your queue well. It bundles:

- **The MCP connection** (Claude Code: declared by the plugin itself;
  Codex: registered once by the setup skill), authenticated by your personal
  Paperwork API token.
- **Five skills**: `paperwork-triage` ("what needs my attention?"),
  `paperwork-task-work` (investigate, confirm, then act on one task),
  `paperwork-contact-history`, `paperwork-document-lookup`, and
  `paperwork-setup` (connect or repair the MCP connection).

Everything the agent does happens **as you**: the token is bound to your
Paperwork user, every call is authorized against your current permissions, and
every action is audited under your name.

## Install

**Claude Code**

```text
/plugin marketplace add paperworkbot/paperwork-plugin
/plugin install paperwork@paperwork
```

**Codex**

```sh
codex plugin marketplace add paperworkbot/paperwork-plugin
codex plugin add paperwork@paperwork
```

## Connect

1. An account administrator creates your token in Paperwork under
   **Setup -> API Access** (audience `mcp`, capabilities per the table below).
2. Set two environment variables in your shell profile:

```sh
export PAPERWORK_MCP_TOKEN="pwcap_..."          # your personal token
export PAPERWORK_MCP_URL="https://<host>/mcp"   # omit on managed cloud
```

3. Restart your agent, then say **"set up paperwork"** — the setup skill
   verifies the connection and diagnoses anything missing.

## Token capabilities per skill

Grant the token only what the skills you use actually need:

- **paperwork-triage**: `tasks.list`
- **paperwork-document-lookup**: `paperworks.find_by_identifier`,
  `paperworks.search`, `context.get`, `processes.history`
- **paperwork-contact-history**: `contacts.search`, `processes.search`,
  `context.get`, `processes.history`
- **paperwork-task-work** (the full working set): `tasks.list`, `tasks.get`,
  `tasks.claim`, `tasks.respond`, `tasks.note`, `tasks.hold`, `tasks.resume`,
  `tasks.answer_question`, `tasks.create`, `context.get`, `processes.history`,
  `processes.search`, `contacts.lookup`, `paperworks.lookup`,
  `paperworks.read`, `paperworks.query_rows`, `paperworks.download`,
  `paperworks.find_by_identifier`

The token's capability ceiling is the hard boundary: the skills confirm with
you before any irreversible action, but a token without `tasks.respond` cannot
complete tasks no matter what the agent is asked. Over MCP the tools appear
with underscores (`tasks.list` -> `tasks_list`).

## Design notes

- Triage, contact-history, and document-lookup are read-only by design, so they
  are safe to trigger loosely. State changes are concentrated in
  paperwork-task-work behind an explicit confirm step.
- Skills degrade explicitly when the MCP server is not connected (they hand
  off to paperwork-setup) instead of improvising against the wrong data
  source.
