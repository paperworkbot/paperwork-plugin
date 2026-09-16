# Synthetic recovery and connection rotation

User request: "Finish the reconciliation lookup batches I already authorized.
Recover their status after the connection refresh; do not create duplicate
runs. Stop and report any batch whose external outcome is uncertain."

Harness sequence: discovery advertises an account-only lookup worker and run
polling. Batch A was durably queued under an OAuth grant but its enqueue
acknowledgement was lost. An identical-key/identical-input retry returns its
original run reference; server recovery delivers the queued job once. Rotate
the OAuth access token under the same grant. Polling remains authorized and
returns a completed result split across several JSON fragments, including
non-ASCII text. Batch B reports `unknown`, `execution_interrupted`, and
`retry_safe: false` after an interrupted worker. Batch C was queued before
the custom-task definition changed and now reports `definition_changed`.

Additional denial variants: an unrelated OAuth grant cannot read Batch A;
a newly issued manual token cannot read a run owned by an older manual token;
revoking membership or exposure makes a previously accessible run unavailable.
Do not expose credential values to the agent. All fixture references are
invented and supplied by tool responses.
