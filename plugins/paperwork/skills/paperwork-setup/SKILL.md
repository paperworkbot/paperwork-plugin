---
name: paperwork-setup
description: Connect this agent to Paperwork, or diagnose a broken Paperwork MCP connection. Use when the user says "set up paperwork", "connect paperwork", the Paperwork tools are missing, or a Paperwork tool call fails with an authentication or connection error.
---

# Set Up the Paperwork Connection

Get the Paperwork MCP connection working for this user, on this machine.

The Paperwork tools (named like `tasks_list`) come from a streamable HTTP MCP
server at the user's Paperwork host, authenticated by a personal API token.
Two environment variables drive everything:

- `PAPERWORK_MCP_URL` — `https://<their-paperwork-host>/mcp`. Cloud users can
  omit it; the default points at the managed cloud. Self-hosted users must set
  it to their own host.
- `PAPERWORK_MCP_TOKEN` — a `pwcap_...` token from **Setup -> API Access** in
  Paperwork, created by an account administrator, bound to the user's own
  account identity.

## Procedure

1. **Check whether it already works.** If Paperwork tools are available, call
   `tasks_list` with `{"limit": 1}`. Success means the connection is fine —
   report that and stop.
2. **Diagnose a failure** by its shape:
   - Tools missing entirely → the MCP server is not registered (step 3).
   - `unauthorized` → token missing, expired, revoked, or its user was
     deactivated. The user needs a fresh token from **Setup -> API Access**;
     remind them tokens expire (up to 365 days) and are shown only once.
   - `forbidden` on one specific tool → the token's capability ceiling does not
     include that capability. The administrator must grant it on a new token —
     the plugin README lists which capabilities each skill needs.
   - Connection refused / DNS errors → wrong `PAPERWORK_MCP_URL`, or their
     deployment has not enabled the API (`PAPERWORK_CAPABILITIES_API_ENABLED`).
3. **Register or repair the connection.** Ask the user for their Paperwork host
   (unless cloud) and confirm they have a token before touching config:
   - Environment variables belong in the user's shell profile. With their
     consent, append exports of `PAPERWORK_MCP_URL` and `PAPERWORK_MCP_TOKEN`;
     never echo the token back into the conversation afterwards.
   - **Claude Code**: the plugin already declares the MCP server using those
     variables — after setting them, the user restarts Claude Code. Without the
     plugin: `claude mcp add --transport http paperwork <url> --header
     "Authorization: Bearer <token>"`.
   - **Codex**: `codex mcp add paperwork --url <url> --bearer-token-env-var
     PAPERWORK_MCP_TOKEN`.
4. **Verify** with `tasks_list` `{"limit": 1}` (after a client restart when the
   variables are new), and tell the user what worked.

## Rules

- The token is a credential: never print it into chat, notes, files other than
  the user's own shell profile, or command output the user did not ask for.
- Never guess a host. Ask.
- If the user has no token, walk them to **Setup -> API Access** in their
  Paperwork instance; an account administrator creates it and picks the
  capability ceiling there. Do not improvise other ways to authenticate.
