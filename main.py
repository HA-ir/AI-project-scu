from game import Game
from renderer import GameRenderer

from test_agents import GreedyAgent, BlockerAgent
from my_agents import  MyAgent

def run_game(with_renderer: bool = True, fps: int = 3):

    game = Game(BlockerAgent(), MyAgent())

    if with_renderer:
        renderer = GameRenderer(fps=fps)
        try:
            winner = game.play(renderer=renderer)
        finally:
            renderer.close()
    else:
        winner = game.play()

    if winner > 0:
        print(f"Player {winner} wins!")


if __name__ == "__main__":
    run_game()
