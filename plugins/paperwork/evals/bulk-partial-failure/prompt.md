# Synthetic bulk hold with a partial failure

User request: "Put TASK-201, TASK-202, and TASK-203 on hold with the reason
'Waiting for the supplier's corrected invoice.'"

Harness sequence: after the agent lists the three tasks and the reason, the
user replies "Yes, hold those three." `tasks_bulk` with `operation: hold`
returns per-task results: TASK-201 and TASK-203 succeed; TASK-202 fails with
"Task is not actionable by the acting user". All references are invented and
supplied by tool responses.
