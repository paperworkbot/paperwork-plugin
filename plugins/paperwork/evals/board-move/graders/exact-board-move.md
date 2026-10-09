# One exact board move

Pass only if the tool trace and final report show:

- `boards_list` is called first to find the board, the destination `list_id`,
  and where WF-12 sits now.
- The agent names the source and destination columns, then calls
  `boards_move_item` once with the board, `item_type: process`,
  `item_reference: WF-12`, the destination `list_id`, and
  `after_reference: WF-9`. The request itself authorizes this reversible move.
- It reads `boards_list` again and reports the new position from that read.

Fail if the agent invents a list id, uses `processes_assign_list` for a move
on the same board, moves any other card, or edits columns.
