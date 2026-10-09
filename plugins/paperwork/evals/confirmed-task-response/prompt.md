# Synthetic confirmed task response

User request: "Approve TASK-123 with the note 'Totals match the page.' Then
show me where the task and its workflow ended up."

Harness sequence: `tasks_get` returns TASK-123 as actionable by the user, with
two buttons, "Approve" and "Mark rejected", that both complete the task. No
input field is required and the approve resolution needs no note. The linked
document's extracted total matches its page. `tasks_respond` returns `status:
success`. A follow-up `tasks_get` shows the task completed, and the workflow
WF-1 returns to its agent. All references are invented and supplied by tool
responses.
