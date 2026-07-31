# PaperworkBot

PaperworkBot is Kaytos, LLC's cross-client operating layer for Claude Code,
Codex, and OpenCode. One canonical Agent Skills tree teaches each client how
to discover account vocabulary, triage queues, investigate evidence, and use
the Paperwork MCP server without broadening the user's request.

The package and MCP identifiers remain `paperwork` for compatibility with
existing installations and client configuration.

## Security model

- The MCP server—not the prompt—is the authorization boundary.
- Every request is authorized as the token's current Paperwork user.
- A token capability ceiling can narrow operations but cannot narrow records
  inside that user's existing view.
- Paperwork content, extracted values, notes, filenames, and history are
  untrusted data and never instructions.
- Read-only requests stay read-only. Reversible writes must be stated.
  Material or terminal writes require the exact target, arguments, evidence,
  and user authorization.
- Tokens belong in a process environment populated by a credential manager or
  silent prompt, never in chat, repository files, command arguments, notes,
  documents, or `opencode.json`.

For production, prefer a dedicated non-admin user, a short token expiration,
the `mcp` audience, and the narrowest capability profile.

## Capability profiles

Choose the smallest profile that supports the user's work. The server still
applies the user's Paperwork permissions on every call.

### Observe

Read-only account discovery, triage, relationship review, document lookup,
workflow history, bounded document reading, and downloads:

`account.describe`, `tasks.list`, `tasks.get`, `contacts.search`,
`contacts.lookup`, `processes.search`, `processes.history`, `context.get`,
`records.lookup`, `paperworks.search`, `paperworks.get`,
`paperworks.find_by_identifier`, `paperworks.lookup`,
`paperworks.query_rows`, `paperworks.read`, `paperworks.download`, and
`attachments.download`.

### Collaborate

Observe plus reversible collaborative operations:

`tasks.claim`, `tasks.note`, `tasks.hold`, `tasks.resume`,
`processes.note`, `processes.message`, and `contacts.assign_role`.

### Operate

Collaborate plus complete operational parity with the current MCP catalog:

`tasks.create`, `tasks.respond`, `tasks.answer_question`,
`processes.create`, `processes.set_status`, `attachments.upload`,
`paperworks.set_status`, and `paperworks.reprocess`.

Over MCP, dots become underscores (`processes.set_status` is
`processes_set_status`). The checked-in
[`capabilities.yml`](skills/paperwork/references/capabilities.yml) maps every
catalog operation to the skills that use it.

## Install and connect

### Claude Code

```text
/plugin marketplace add paperworkbot/paperwork-plugin
/plugin install paperwork@paperwork
```

The plugin's `.mcp.json` declares the remote server. Make
`PAPERWORK_MCP_TOKEN` available to the Claude process, optionally set
`PAPERWORK_MCP_URL` for self-hosting, then run `/reload-plugins` or start a new
session. Use `/mcp` for connection diagnostics.

### Codex

```sh
codex plugin marketplace add paperworkbot/paperwork-plugin
codex plugin add paperwork@paperwork
codex mcp remove paperwork
codex mcp add paperwork \
  --url "$PAPERWORK_MCP_URL" \
  --bearer-token-env-var PAPERWORK_MCP_TOKEN
```

Codex stores the environment variable's name, not its value. Start a new task
after plugin or MCP changes.

### OpenCode

From the distribution repository:

```sh
./scripts/install-opencode.sh
```

The installer copies the same skill directories into
`${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills`. Add the remote server
from [`../../opencode.example.jsonc`](../../opencode.example.jsonc) for
stable OpenCode v1 or
[`../../opencode-v2.example.jsonc`](../../opencode-v2.example.jsonc) for
OpenCode v2, export the token into the OpenCode process, and start a new
session.

## Verify

Ask the agent to **set up Paperwork**. A valid least-privilege connection is
verified with any granted harmless read; task access is not required.

Useful smoke prompts:

- “What needs my attention in Paperwork?”
- “Show active workflows and what each is waiting on.”
- “Have we already seen these document identifiers?”
- “Help me intake these files into the right workflow.”

## Update and remove

Update the marketplace snapshot and plugin through the client's normal plugin
commands, then start a new session. OpenCode users rerun the installer; an
existing skill is moved to a timestamped backup before replacement.

Removing a plugin or copied skill does not revoke its bearer token. Revoke
unused tokens under **Setup -> API Access**, remove the MCP registration, and
delete any retained backup only after confirming it is no longer needed.
