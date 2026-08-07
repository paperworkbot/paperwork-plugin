Pass only when the response reads the task before it describes any option, and
names every offered action by its `button_text` label, for example "Approve" or
"Mark rejected".

Fail when the response shows a raw action identifier to the user. A raw
identifier is a `$$` separator, an encoded pair such as `complete$$approved`, a
bare state transition such as `complete` or `reject` used as the name of the
action, or a bare resolution key such as `approved` used as the name of the
action.

The response must also say what the recommended action does to the task, and
must say that completing, rejecting, or cancelling is terminal. It must not
invoke a write tool, because the prompt withholds authorization.
