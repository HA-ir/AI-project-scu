from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional
from collections import deque
from utils import translate_direction, translate_move, translate_wall, wall_cells

if TYPE_CHECKING:
    from game import GameState, AgentState
    from typing import Union
    _State = Union[GameState, AgentState]


def has_path(start_row: int, start_col: int, goal_row: int, goal_col: Optional[int], board) -> bool:
    visited = {(start_row, start_col)}
    queue = deque([(start_row, start_col)])
    moves = [(-2, 0, -1, 0), (2, 0, 1, 0), (0, -2, 0, -1), (0, 2, 0, 1)]
    while queue:
        current_row, current_col = queue.popleft()
        if (current_row == goal_row) if goal_col is None else (current_row == goal_row and current_col == goal_col):
            return True
        for d_row, d_col, w_row, w_col in moves:
            next_row, next_col = current_row + d_row, current_col + d_col
            if 0 <= next_row <= 16 and 0 <= next_col <= 16 and (next_row, next_col) not in visited:
                if board[current_row + w_row][current_col + w_col] == "":
                    visited.add((next_row, next_col))
                    queue.append((next_row, next_col))
    return False


def validate_move(state: _State, direction: str,  need_translate:bool = True) -> bool:
    if need_translate:
        direction = translate_direction(direction)
        
    deltas = {"U": (-2, 0, -1, 0), "D": (2, 0, 1, 0), "L": (0, -2, 0, -1), "R": (0, 2, 0, 1)}
    if direction not in deltas:
        return False
    if state.turn == 1:
        p_row, p_col, o_row, o_col = state.player1_row, state.player1_col, state.player2_row, state.player2_col
    else:
        p_row, p_col, o_row, o_col = state.player2_row, state.player2_col, state.player1_row, state.player1_col
    d_row, d_col, w_row, w_col = deltas[direction]
    next_row, next_col = p_row + d_row, p_col + d_col
    wall_row, wall_col = p_row + w_row, p_col + w_col
    if not (0 <= wall_row <= 16 and 0 <= wall_col <= 16) or state.board[wall_row][wall_col] != "":
        return False
    if not (0 <= next_row <= 16 and 0 <= next_col <= 16):
        return False
    if next_row == o_row and next_col == o_col:
        jump_row, jump_col = next_row + d_row, next_col + d_col
        jump_wall_row, jump_wall_col = next_row + w_row, next_col + w_col
        return (0 <= jump_wall_row <= 16 and 0 <= jump_wall_col <= 16 and
                state.board[jump_wall_row][jump_wall_col] == "" and
                0 <= jump_row <= 16 and 0 <= jump_col <= 16)
    return True


def validate_wall(state: _State, row: int, col: int, orientation: Literal["H", "V"],
                  p1_goal_row: int = 16, p1_goal_col: Optional[int] = None,
                  p2_goal_row: int = 0,  p2_goal_col: Optional[int] = None, need_translate:bool = True) -> bool:
    if need_translate:
        row, col, orientation = translate_wall(row, col, orientation)
    
    my_walls = state.player1_walls if state.turn == 1 else state.player2_walls
    if my_walls <= 0:
        return False
    if orientation == "H" and not (0 <= row <= 7 and 0 <= col <= 7):
        return False
    if orientation == "V" and not (1 <= row <= 8 and 0 <= col <= 7):
        return False
    if orientation not in ("H", "V"):
        return False

    cells = wall_cells(row, col, orientation)
    board = state.board
    if any(board[r][c] != "" for r, c in cells):
        return False

    for r, c in cells:
        board[r][c] = "W"
    ok = (has_path(state.player1_row, state.player1_col, p1_goal_row, p1_goal_col, board) and
          has_path(state.player2_row, state.player2_col, p2_goal_row, p2_goal_col, board))
    for r, c in cells:
        board[r][c] = ""
    return ok