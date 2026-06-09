from __future__ import annotations

from game import Agent
from validation import validate_wall

from typing import TYPE_CHECKING, Optional, Tuple
if TYPE_CHECKING:
    from game import AgentState

from collections import deque


def bfs_next_move(start_row: int, start_col: int, goal_row: int, board) -> Optional[str]:
    moves = [
        ("U", -2, 0, -1, 0),
        ("D",  2, 0,  1, 0),
        ("L",  0, -2, 0, -1),
        ("R",  0,  2, 0,  1),
    ]
    queue = deque([(start_row, start_col, None)])
    visited = {(start_row, start_col)}
    
    while queue:
        row, col, first = queue.popleft()
        if row == goal_row:
            return first
        for direction, dr, dc, wr, wc in moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr <= 16 and 0 <= nc <= 16 and (nr, nc) not in visited:
                if board[row + wr][col + wc] == "":
                    visited.add((nr, nc))
                    queue.append((nr, nc, first or direction))
    return None


class GreedyAgent(Agent):
    def make_decision(self, state: AgentState):
        if state.turn == 1:
            my_row, my_col, my_goal = state.player1_row, state.player1_col, 16
        else:
            my_row, my_col, my_goal = state.player2_row, state.player2_col, 0
        
        direction = bfs_next_move(my_row, my_col, my_goal, state.board)
        default = "D" if state.turn == 1 else "U"  
        return ("move", direction or default)


class BlockerAgent(Agent):
    def make_decision(self, state: AgentState): 
        if state.turn == 1:
            my_row, my_col, my_goal, my_walls = state.player1_row, state.player1_col, 16, state.player1_walls
            opp_row, opp_col, opp_goal = state.player2_row, state.player2_col, 0
        else:
            my_row, my_col, my_goal, my_walls = state.player2_row, state.player2_col, 0, state.player2_walls
            opp_row, opp_col, opp_goal = state.player1_row, state.player1_col, 16
 
        if my_walls > 3:
            wall = self._find_blocking_wall(opp_row, opp_col, opp_goal, state)
            if wall:
                return ("wall", wall)
 
        direction = bfs_next_move(my_row, my_col, my_goal, state.board)
        default = "D" if state.turn == 1 else "U"
        return ("move", direction or default)

    def _find_blocking_wall(self, o_row: int, o_col: int, o_goal: int, state) -> Optional[Tuple[int, int, str]]:
        o_dir = bfs_next_move(o_row, o_col, o_goal, state.board)
        if not o_dir:
            return None

        wr, wc = o_row // 2, o_col // 2      
        candidates = []
        if o_dir == "D":
            candidates = [(wr, wc, "H"), (wr, max(wc - 1, 0), "H")]
        elif o_dir == "U":
            candidates = [(max(wr - 1, 0), wc, "H"), (max(wr - 1, 0), max(wc - 1, 0), "H")]
        elif o_dir == "R":
            candidates = [(wr, wc, "V"), (max(wr - 1, 0), wc, "V")]
        elif o_dir == "L":
            candidates = [(wr, max(wc - 1, 0), "V"), (max(wr - 1, 0), max(wc - 1, 0), "V")]

        for row, col, orient in candidates:
            if validate_wall(state, row, col, orient):
                return (row, col, orient)
        return None