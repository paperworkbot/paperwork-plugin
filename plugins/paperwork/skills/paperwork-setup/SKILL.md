---
name: paperwork-setup
description: Install, connect, verify, diagnose, rotate, or remove the Paperwork MCP connection for Claude Code, Codex, or OpenCode. Use when Paperwork tools are missing, authentication fails, one tool is forbidden, a host changes, a token must be rotated, or the user asks to set up PaperworkBot.
---

# Set Up PaperworkBot

Connect a local agent to the user's Paperwork host through sessionless
Streamable HTTP MCP.

## Normal User Setup

The plugin declares Paperwork as an OAuth MCP server. It connects to the
managed cloud at `https://paperwork.bot/mcp` unless Claude Code is started
with `PAPERWORK_MCP_URL` set (see Self-Hosted Paperwork below). After
installation, use the client's authentication action:

1. Choose **Authenticate**, **Connect**, or **Log in** for Paperwork, depending
   on the client.
2. Sign in to Paperwork in the browser.
3. Review the client name, the acting user, and the account.
4. Choose the access level and, optionally, the agents (see below).
5. Choose **Allow access**.
6. Return to the client and start a new task if its tool catalog was already
   open.

Do not ask a user to create, copy, or export a token for a browser connection.
The client stores short-lived OAuth credentials in its own credential store and
refreshes them automatically.

## Access Level And Agent Limit

The consent screen asks for an access level. The default lets the local
agent do everything the user can do in the Paperwork UI, under the user's own
permissions. Keep the default unless the user wants a narrower connection:

| Access level | Allows |
| --- | --- |
| **Everything my roles allow** (`setup`, the default) | Every tool except account data. The user's roles still decide each call, so agent instructions, SOPs, learnings, and task-kind management work only when the user can edit them in the UI. Task-kind management requires account-admin rights. |
| **Tasks and workflows only** (`work`) | Read, plus everyday writes: respond to and hold tasks, add notes, move and assign workflows, correct documents, edit contacts. No agent instructions, SOPs, or learning writes. |
| **Read only** (`read`) | Look at tasks, workflows, documents, and contacts. No writes. |

- Suggest `work` or `read` only when the user asks for a narrower connection,
  for example a read-only check-in. Do not narrow by default.
- **Also allow account data access** is a separate checkbox for `data_*`
  tools. Leave it off unless the user needs bulk data analysis.
- **Limit to agents** is optional. Checked agents limit the connection to
  their workflows, tasks, documents, and attachments. Leave all unchecked to
  allow every agent the user can open. Contacts, boards, and SOPs are not
  narrowed.
- To change the level or the agents, disconnect and connect again. Refreshing
  a connection never adds access.
- A browser connection made before access levels existed keeps its stored
  ceiling; one with no stored ceiling gets the default (everything the user's
  roles allow, without account data).
- If the screen says the connection returns to a host that is not this
  computer, continue only if the user expected that host.

## Check First

1. If any Paperwork tools are already available, the MCP catalog authenticated.
2. When a harmless read tool is granted, verify with the first suitable call:
   `account_describe`, `tasks_list {"limit": 1}`,
   `paperworks_search {"limit": 1}`, or
   `processes_search {"limit": 1}`.
3. Do not require `tasks_list`: least-privilege document or workflow tokens may
   intentionally omit it. Tool discovery plus a successful granted read is
   sufficient.

## Diagnose

- **No tools or connection refused:** server is not registered, URL is wrong,
  DNS/TLS failed, or the deployment has not enabled
  `PAPERWORK_CAPABILITIES_API_ENABLED`.
- **Endpoint not found:** the server version or feature flag does not expose
  `/mcp`.
- **Unauthorized:** choose the client's Paperwork authentication action. If
  already connected, disconnect and authorize again. For a manual token
  connection, the token may be missing, expired, revoked, or bound to a
  disabled user.
- **Forbidden on one tool, or the tool is missing:** the connection is
  healthy, but its access level, a manual token's capability list, or the
  acting user's current Paperwork permission denies that capability. For a
  setup write on a narrowed connection, reconnect with the default,
  **Everything my roles allow**.
- **"This connection is limited to other agents", or a workflow is not
  found:** the connection has an agent limit that excludes that record.
  Reconnect with a different agent selection if the user needs it.
- **New tools missing after an upgrade:** an OAuth access token snapshots the
  registry when issued. Refresh or reconnect, then rediscover tools. Issuance
  and refresh use the current registry within the connection's access level,
  subject to current user permissions. Manual tokens instead need explicit
  capability grants. Same-grant refresh preserves run continuity;
  fresh authorization may create a new connection. Retain pending run
  references and resolve continuity before replacing their owning connection.
  Neither refresh nor reconnect bypasses a role or record-access denial.
- **Not found on one record:** do not treat this as connection failure; the
  record may be absent or outside the user's authorized view.
- **Rate limited:** honor `Retry-After`; do not rotate credentials or retry in a
  tight loop.

Use [the capability map](../paperwork/references/capabilities.yml) to identify
the missing grant and its owning workflow skill.

## Codex

Install the plugin from the marketplace. In **Settings -> MCP servers**, open
Paperwork and choose **Authenticate**. Codex opens Paperwork in the
browser and stores the resulting OAuth credentials in its credential store.
Start a new Codex task after connecting.

The Codex plugin server always points at the managed cloud: Codex does not
expand environment variables in a plugin's MCP file. For a self-hosted
deployment, disable the plugin's Paperwork server and register your own:

```sh
codex mcp add paperwork-selfhosted --url https://paperwork.example.com/mcp \
  --oauth-resource https://paperwork.example.com/mcp
codex mcp login paperwork-selfhosted
```

Use the deployment's canonical application host, not an account subdomain.
For headless use, replace the login with `--bearer-token-env-var
PAPERWORK_MCP_TOKEN` and a manual token.

Paperwork advertises MCP read/write annotations so Codex can auto-approve
trusted reads while continuing to gate state-changing tools. Do not set a
blanket `approve` policy for every Paperwork tool.

## Claude Code

The installed plugin declares the OAuth server in `.mcp.json`. Use `/mcp`,
choose Paperwork, and authenticate in the browser. Run `/reload-plugins` or
start a new session if tools do not appear after authorization.

Do not add a second manual `paperwork` MCP server when the plugin server is
enabled; duplicate catalogs confuse tool selection.

### Self-Hosted Paperwork In Claude Code

The plugin reads the server URL from `PAPERWORK_MCP_URL` and falls back to the
managed cloud when it is not set. For a self-hosted deployment:

1. Get the deployment's absolute `/mcp` URL from its administrator, for
   example `https://paperwork.example.com/mcp`. Use the canonical application
   host, not an account subdomain. Never guess a self-hosted host.
2. Set `PAPERWORK_MCP_URL` to that URL in the environment that starts Claude
   Code, for example the shell profile or the organization's managed
   environment.
3. Start Claude Code again, open `/mcp`, choose Paperwork, and authenticate in
   the browser against the self-hosted deployment. Browser OAuth works the
   same way as in the cloud; no token is needed.
4. Verify with one read, as in Check First.

To return to the managed cloud, unset `PAPERWORK_MCP_URL` and start Claude
Code again.

## Claude App, Web, Mobile, And Cowork

Paperwork is a remote connector, so it is configured through the user's Claude
account rather than a desktop configuration file:

1. Open **Customize -> Connectors**.
2. Choose **Add custom connector**.
3. Enter `https://paperwork.bot/mcp`.
4. Choose **Connect**, sign in to Paperwork, and approve access.

Do not ask for an OAuth client ID or secret. Paperwork supports dynamic client
registration. Team and Enterprise plans require an Owner to add the custom
connector under **Organization settings -> Connectors** before members can
connect their own Paperwork accounts.

## Manual Tokens For Automation

Use a manual token only for headless automation or a client without MCP OAuth,
such as OpenCode.

- `PAPERWORK_MCP_URL`: the deployment's absolute `/mcp` URL. Never guess a
  self-hosted host.
- `PAPERWORK_MCP_TOKEN`: a one-time `pwcap_...` value issued under
  **Setup -> API & MCP Access**, bound to one user and carrying the `mcp`
  audience.

The token is a bearer credential. Never ask the user to paste it into chat and
never echo it after entry. Prefer an OS credential manager or a silent prompt
that populates the client process environment. Do not put the token in command
arguments, repository files, `opencode.json`, task notes, or documents.

A manual token lists its capabilities one by one and can also be limited to
named agents (Setup -> API & MCP Access -> **Limit to Agents**). Grant only
what the automation needs.

For Codex, remove or disable the managed-cloud plugin server before registering
a self-hosted server with `--bearer-token-env-var PAPERWORK_MCP_TOKEN`; duplicate
catalogs confuse tool selection.

## OpenCode

Install the shared skills with the distribution repository's
`scripts/install-opencode.sh`, then add a remote `paperwork` entry to
`opencode.json`.

Stable OpenCode v1 uses a direct entry under `mcp`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "paperwork": {
      "type": "remote",
      "url": "https://your-paperwork-host.example/mcp",
      "enabled": true,
      "oauth": false,
      "headers": {
        "Authorization": "Bearer {env:PAPERWORK_MCP_TOKEN}"
      }
    }
  }
}
```

OpenCode v2 nests named servers under `mcp.servers` and no longer uses the
v1 `enabled` field:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "paperwork": {
        "type": "remote",
        "url": "https://your-paperwork-host.example/mcp",
        "headers": {
          "Authorization": "Bearer {env:PAPERWORK_MCP_TOKEN}"
        }
      }
    }
  }
}
```

OpenCode discovers the same skills from its global skills directory and
substitutes the token from the environment. Use `opencode mcp list` when the
installed version provides MCP diagnostics.

## Disconnect, Rotate, Or Remove

For OAuth, use the client's **Disconnect** action and reconnect if needed.
Paperwork access also stops immediately when the acting user is deactivated.

For a manual token, issue a replacement with the same or narrower grants,
update the client credential without printing it, verify one read, and revoke
the prior token under **Setup -> API & MCP Access**.

## Production Guidance

OAuth runs as the person who approved access and remains bounded by that
person's current roles, the chosen access level, and any agent limit. For
unattended manual-token automation, use a dedicated non-admin Paperwork user
whose roles bound record access, and limit the token to the agents it serves.
