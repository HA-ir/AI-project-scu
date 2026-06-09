from __future__ import annotations
from abc import ABC, abstractmethod
import threading
from dataclasses import dataclass, field
from typing import List, Literal

from utils import translate_move, translate_walls_set, walls_to_board

WALLS = 10
DECISION_TIME_LIMIT = 3.0


def _timed_decision(agent, state, timeout: float = DECISION_TIME_LIMIT):
    """Run agent.make_decision in a daemon thread; return None if timeout or exception."""
    result: list = [None]

    def _run():
        try:
            result[0] = agent.make_decision(state)
        except Exception:
            pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout)
    return result[0]


def _make_board():
    return [["" for _ in range(17)] for _ in range(17)]


@dataclass
class GameState:
    player1_row: int
    player1_col: int
    player1_walls: int
    player2_row: int
    player2_col: int
    player2_walls: int
    turn: Literal[1, 2]
    board: List[List[str]] = field(default_factory=_make_board)
    walls: frozenset = field(default_factory=frozenset)

    def to_agent_state(self) -> AgentState:
        if self.turn == 1:
            return AgentState(
                player1_row=self.player1_row, player1_col=self.player1_col,
                player1_walls=self.player1_walls,
                player2_row=self.player2_row, player2_col=self.player2_col,
                player2_walls=self.player2_walls,
                turn=1, walls=self.walls,
            )
        else:
            return AgentState(
                player1_row= 16 - (self.player2_row), player1_col= 16 - (self.player2_col),
                player1_walls=self.player2_walls,
                player2_row= 16 - (self.player1_row), player2_col= 16 - (self.player1_col),
                player2_walls=self.player1_walls,
                turn=1, walls=translate_walls_set(self.walls),
            ) 
            


@dataclass(frozen=True)
class AgentState:
    """Immutable, hashable state passed to agents. Safe for transposition tables."""
    player1_row: int
    player1_col: int
    player1_walls: int
    player2_row: int
    player2_col: int
    player2_walls: int
    turn: Literal[1, 2]
    walls: frozenset  # frozenset of (row, col, orientation) — one tuple per placed wall

    @property
    def board(self) -> List[List[str]]:
        board = walls_to_board(self.walls)
        board[self.player1_row][self.player1_col] = "P1"
        board[self.player2_row][self.player2_col] = "P2"
        return board


class Agent(ABC):
    @abstractmethod
    def make_decision(self, state: AgentState): ...



class Game:
    def __init__(self, agent1, agent2):
        self.agent1 = agent1
        self.agent2 = agent2
        self.state = GameState(
            player1_row=0,  player1_col=8,  player1_walls=WALLS,
            player2_row=16, player2_col=8,  player2_walls=WALLS,
            turn=1,
        )

    def place_wall(self, row: int, col: int, orientation: Literal["H", "V"]):
        from validation import validate_wall, wall_cells
        state = self.state
        if not validate_wall(state, row, col, orientation, need_translate=False):
            raise ValueError("Invalid wall placement!")
        for r, c in wall_cells(row, col, orientation):
            state.board[r][c] = f"W{state.turn}"
        state.walls = state.walls | frozenset({(row, col, orientation)})
        if state.turn == 1:
            state.player1_walls -= 1
        else:
            state.player2_walls -= 1

    def move(self, direction: str):
        from validation import validate_move
        state = self.state
        if not validate_move(state, direction, need_translate=False):
            raise ValueError("Invalid move!")
        d_row, d_col = {"U": (-2, 0), "D": (2, 0), "L": (0, -2), "R": (0, 2)}[direction]
        if state.turn == 1:
            p_row, p_col = state.player1_row, state.player1_col
            o_row, o_col = state.player2_row, state.player2_col
        else:
            p_row, p_col = state.player2_row, state.player2_col
            o_row, o_col = state.player1_row, state.player1_col
        n_row, n_col = p_row + d_row, p_col + d_col
        if n_row == o_row and n_col == o_col:
            n_row, n_col = n_row + d_row, n_col + d_col
        if state.turn == 1:
            state.player1_row, state.player1_col = n_row, n_col
        else:
            state.player2_row, state.player2_col = n_row, n_col

    def play(self, renderer=None) -> int:
        while True:
            state = self.state
            agent = self.agent1 if state.turn == 1 else self.agent2
            decision = _timed_decision(agent, state.to_agent_state())
            if decision is not None:
                try:
                    action, params = translate_move(self.state.turn, *decision)
                    if action == "move":
                        self.move(params)
                    elif action == "wall":
                        self.place_wall(*params)
                    if state.turn == 1:        
                        print(f"player red:", f"[{action, params}]", f"------ row:{state.player1_row}, cell:{state.player1_col}")
                    else:
                        print(f"player blue:", f"[{action, params}]", f"------ row:{state.player2_row}, cell:{state.player2_col}")
                        
                        
                except Exception as e:
                    print(e)

            if renderer is not None and not renderer.render(state):
                return -1

            if state.player1_row == 16:
                if renderer: renderer.show_winner(1)
                return 1
            if state.player2_row == 0:
                if renderer: renderer.show_winner(2)
                return 2

            state.turn = 2 if state.turn == 1 else 1     