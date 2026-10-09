# Synthetic board move

User request: "On the Accounts Payable board, move WF-12 into the Waiting on
Supplier column, right after WF-9."

Harness sequence: `boards_list` for that board returns its columns with list
ids and positions, and shows WF-12 in the Inbox column and WF-9 in Waiting on
Supplier. `boards_move_item` succeeds. A second `boards_list` shows WF-12
directly after WF-9. All references are invented and supplied by tool
responses.
