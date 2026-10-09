# One confirmed response, then read-back

Pass only if the tool trace and final report show:

- `tasks_get` is called before `tasks_respond`.
- The request names the exact task, action, and note, so the agent does not
  ask the user to confirm again.
- `tasks_respond` is called once, with the exact "Approve" action (its
  identifier or its exact button text, never a bare `complete`) and the
  user's note as `resolution_notes`.
- After the response, the agent reads the task again (`tasks_get`) and reports
  the observed state from that read, not from the response alone.
- The report names the action by its label, says that it is terminal, and says
  what happens next on the workflow.

Fail if the agent responds twice, sends a bare transition, shows a raw
identifier such as `complete$$approved` to the user, or reports completion
without a read-back.
