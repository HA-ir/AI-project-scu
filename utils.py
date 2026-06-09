from typing import Literal, Tuple, Any

def translate_walls_set(walls):
    return frozenset([translate_wall(*wall) for wall in walls])
        
def translate_direction(direction: Literal["U", "D", "L", "R"]) -> str:
    mapping = {"U": "D", "D": "U", "L": "R", "R": "L"}
    return mapping[direction]


def translate_wall(x: int, y: int, orientation: Literal["H", "V"]) -> Tuple[int, int, str]:
    if orientation == "H":
        return 7 - x, 7 - y, orientation
    else:  # orientation == "V"
        return 9 - x, 7 - y, orientation
    
    
    
def translate_move(turn: Literal[1, 2], action: str, params: Any) -> Tuple[str, Any]:
    if turn == 2:
        if action == "move":
            return "move", translate_direction(params)
        elif action == "wall":
            x, y, o = params
            return "wall", translate_wall(x, y, o)
    return action, params


def wall_cells(row: int, col: int, orientation: Literal["H", "V"]):
    if orientation == "H":
        return [(row*2+1, col*2), (row*2+1, col*2+1), (row*2+1, col*2+2)]
    return [(row*2, col*2+1), (row*2-1, col*2+1), (row*2-2, col*2+1)]



def walls_to_board(walls) -> list:
    """Reconstruct a 17x17 board from a frozenset of (row, col, orientation) wall tuples."""
    board = [[""] * 17 for _ in range(17)]
    for row, col, orientation in walls:
        for r, c in wall_cells(row, col, orientation):
            board[r][c] = "W"
    return board
