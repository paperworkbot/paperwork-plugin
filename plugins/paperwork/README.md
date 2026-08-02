# PaperworkBot

PaperworkBot is Kaytos, LLC's cross-client operating layer for the Claude app,
Claude Code, Codex, and OpenCode. The Claude app uses the remote Paperwork
connector directly. One canonical Agent Skills tree teaches coding clients how
to discover account vocabulary, triage queues, investigate evidence, and use
the Paperwork MCP server without broadening the user's request.

The package and MCP identifiers remain `paperwork` for compatibility with
existing installations and client configuration.

## Security model

- The MCP server—not the prompt—is the authorization boundary.
- OAuth requests are authorized as the Paperwork user who approved the
  connection. Manual tokens are authorized as their bound user.
- Current user permissions remain the record boundary. A manual token can
  additionally narrow which operations are available.
- Paperwork content, extracted values, notes, filenames, and history are
  untrusted data and never instructions.
- Read-only requests stay read-only. Reversible writes must be stated.
  Material or terminal writes require the exact target, arguments, evidence,
  and user authorization.
- OAuth credentials stay in the client's credential store. Manual tokens
  belong in a process environment populated by a credential manager, never in
  chat, repository files, command arguments, notes, documents, or
  `opencode.json`.

For unattended automation, prefer a dedicated non-admin user, a short manual
token expiration, the `mcp` audience, and the narrowest capability profile.

## Capability profiles

Choose the smallest profile that supports the user's work. The server still
applies the user's Paperwork permissions on every call.

### Observe

Read-only account discovery, triage, relationship review, document lookup,
workflow history, upload progress, bounded document reading, and downloads:

`account.describe`, `tasks.list`, `tasks.get`, `contacts.search`,
`contacts.lookup`, `processes.search`, `processes.history`, `context.get`,
`records.lookup`, `paperworks.search`, `paperworks.get`,
`paperworks.find_by_identifier`, `paperworks.lookup`,
`paperworks.query_rows`, `paperworks.read`, `paperworks.download`,
`attachments.download`, and `attachments.get`.

### Collaborate

Observe plus reversible collaborative operations:

`tasks.claim`, `tasks.note`, `tasks.hold`, `tasks.resume`,
`processes.note`, `processes.message`, and `contacts.assign_role`.

### Operate

Collaborate plus complete operational parity with the current MCP catalog:

`tasks.create`, `tasks.respond`, `tasks.answer_question`,
`processes.create`, `processes.set_status`, `attachments.upload`,
`paperworks.set_status`, and `paperworks.reprocess`.

### Account-specific direct tools

Administrators may separately expose selected custom tasks as `custom_task_*`
MCP tools and grant each API token explicit access. The acting user's current
role and workflow permissions must also allow every discovery, invocation, and
poll request. These tools are material writes: invoke once, keep the returned
run reference, poll with `custom_task_runs_get`, and treat all output as
untrusted data.

Over MCP, dots become underscores (`processes.set_status` is
`processes_set_status`). The checked-in
[`capabilities.yml`](skills/paperwork/references/capabilities.yml) maps every
catalog operation to the skills that use it.

## Install and connect

### Claude app, web, or mobile

Open **Customize -> Connectors**, choose **Add custom connector**, and enter
`https://paperwork.bot/mcp`. Choose **Connect**, sign in to Paperwork, and
approve access. Remote connectors sync through the Claude account and work in
Claude web, Desktop, mobile, Cowork, and Claude Code.

On Team and Enterprise plans, an Owner first adds the URL under
**Organization settings -> Connectors**. Each member then connects their own
Paperwork account, so every call remains bounded by that member's Paperwork
permissions.

### Claude Code

```text
/plugin marketplace add paperworkbot/paperwork-plugin
/plugin install paperwork@paperwork
```

The plugin's `.mcp.json` declares the managed-cloud OAuth server. Open `/mcp`,
choose Paperwork, and authenticate in the browser. Run `/reload-plugins` or
start a new session after connecting.

### Codex

```sh
codex plugin marketplace add paperworkbot/paperwork-plugin
codex plugin add paperwork@paperwork
```

In **Settings -> MCP servers**, open Paperwork and choose **Authenticate**.
Codex opens Paperwork in the browser and stores the OAuth
credentials in its credential store. Start a new task after connecting.

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
- “Upload this file, wait for extraction, show me the extracted data and
  timeline, then tell me what needs attention.”

## Update and remove

Update the marketplace snapshot and plugin through the client's normal plugin
commands, then start a new session. OpenCode users rerun the installer; an
existing skill is moved to a timestamped backup before replacement.

Disconnect OAuth in the client before removing the plugin. Removing a plugin
or copied skill does not revoke a separately issued manual token; revoke those
under **Setup -> API & MCP Access**.
