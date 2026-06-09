import pygame

BOARD_CELLS = 9
HUD_H       = 52

BG          = (101, 67,  33)
CELL        = (222, 184, 135)
GAP_EMPTY   = (160, 120, 70)
WALL1 = (150, 30, 20)
WALL2       = ( 50, 110, 210)
PAWN1       = (210,  40,  40)
PAWN2       = ( 30,  90, 200)
PAWN_SHINE1 = (240, 110, 110)
PAWN_SHINE2 = (110, 170, 240)
PAWN_RIM    = ( 30,  20,  10)
TEXT        = (255, 255, 255)
HUD_BG      = ( 60,  35,  15)


class GameRenderer:
    def __init__(self, fps: int = 3, screen_usage: float = 0.88):
        pygame.init()

        info = pygame.display.Info()
        avail = min(info.current_w, info.current_h - HUD_H) * screen_usage

        # board_px = CELLS*c + (CELLS-1)*gap + 2*margin
        # with gap = c//5, margin = c//2:
        # board_px ≈ (9 + 8/5 + 1) * c = 11.6 * c
        cell = max(int(avail / 11.6), 20)
        self.C  = cell              # cell size
        self.G  = max(cell // 5, 4) # gap
        self.M  = max(cell // 2, 10) # margin

        self.board_px = BOARD_CELLS * self.C + (BOARD_CELLS - 1) * self.G
        self.W = self.board_px + self.M * 2
        self.H = self.board_px + self.M * 2 + HUD_H

        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Quoridor")
        self.clock = pygame.time.Clock()
        self.fps   = fps

        font_size     = max(cell // 4, 12)
        big_font_size = max(cell // 2, 20)
        self.font     = pygame.font.SysFont("Segoe UI", font_size, bold=True)
        self.big_font = pygame.font.SysFont("Segoe UI", big_font_size, bold=True)

    # ── layout helpers ──────────────────────────────────────────────────────

    def _cell_rect(self, row_idx, col_idx):
        x = self.M + col_idx * (self.C + self.G)
        y = self.M + row_idx * (self.C + self.G)
        return pygame.Rect(x, y, self.C, self.C)

    def _hgap_rect(self, row_idx, col_idx):
        x = self.M + col_idx * (self.C + self.G)
        y = self.M + row_idx * (self.C + self.G) + self.C
        return pygame.Rect(x, y, self.C, self.G)

    def _vgap_rect(self, row_idx, col_idx):
        x = self.M + col_idx * (self.C + self.G) + self.C
        y = self.M + row_idx * (self.C + self.G)
        return pygame.Rect(x, y, self.G, self.C)

    def _inter_rect(self, row_idx, col_idx):
        x = self.M + col_idx * (self.C + self.G) + self.C
        y = self.M + row_idx * (self.C + self.G) + self.C
        return pygame.Rect(x, y, self.G, self.G)

    # ── public API ──────────────────────────────────────────────────────────

    def render(self, game_state) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

        self.screen.fill(BG)
        board = game_state.board

        self._draw_goal_tints()
        self._draw_cells()
        self._draw_gaps(board)
        self._draw_walls(board)
        self._draw_pawn(game_state.player1_row, game_state.player1_col, PAWN1, PAWN_SHINE1)
        self._draw_pawn(game_state.player2_row, game_state.player2_col, PAWN2, PAWN_SHINE2)
        self._draw_hud(game_state)

        pygame.display.flip()
        self.clock.tick(self.fps)
        return True

    def show_winner(self, winner: int):
        color = PAWN1 if winner == 1 else PAWN2
        text  = self.big_font.render(f"Player {winner} wins!", True, color)
        rect  = text.get_rect(center=(self.W // 2, self.H // 2))

        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        bg = pygame.Surface((rect.width + 32, rect.height + 24))
        bg.fill(HUD_BG)
        self.screen.blit(bg, (rect.left - 16, rect.top - 12))
        self.screen.blit(text, rect)

        pygame.display.flip()
        pygame.time.wait(3000)

    def close(self):
        pygame.quit()

    # ── draw helpers ────────────────────────────────────────────────────────

    def _draw_goal_tints(self):
        g1 = pygame.Surface((self.C, self.C), pygame.SRCALPHA)
        g1.fill((255, 180, 120, 90))
        g2 = pygame.Surface((self.C, self.C), pygame.SRCALPHA)
        g2.fill((140, 190, 255, 90))
        for col_idx in range(BOARD_CELLS):
            self.screen.blit(g1, self._cell_rect(BOARD_CELLS - 1, col_idx))
            self.screen.blit(g2, self._cell_rect(0, col_idx))

    def _draw_cells(self):
        r = max(self.C // 12, 2)
        for row_idx in range(BOARD_CELLS):
            for col_idx in range(BOARD_CELLS):
                pygame.draw.rect(self.screen, CELL, self._cell_rect(row_idx, col_idx), border_radius=r)

    def _draw_gaps(self, board):
        r = max(self.G // 3, 1)
        for row_idx in range(BOARD_CELLS - 1):
            for col_idx in range(BOARD_CELLS):
                if not board[row_idx * 2 + 1][col_idx * 2]:
                    pygame.draw.rect(self.screen, GAP_EMPTY, self._hgap_rect(row_idx, col_idx), border_radius=r)
        for row_idx in range(BOARD_CELLS):
            for col_idx in range(BOARD_CELLS - 1):
                if not board[row_idx * 2][col_idx * 2 + 1]:
                    pygame.draw.rect(self.screen, GAP_EMPTY, self._vgap_rect(row_idx, col_idx), border_radius=r)
        for row_idx in range(BOARD_CELLS - 1):
            for col_idx in range(BOARD_CELLS - 1):
                cell  = board[row_idx * 2 + 1][col_idx * 2 + 1]
                color = GAP_EMPTY if not cell else (WALL1 if cell == "W1" else WALL2)
                pygame.draw.rect(self.screen, color, self._inter_rect(row_idx, col_idx))

    def _draw_walls(self, board):
        r = max(self.G // 3, 1)
        for row_idx in range(BOARD_CELLS - 1):
            for col_idx in range(BOARD_CELLS):
                cell = board[row_idx * 2 + 1][col_idx * 2]
                if cell:
                    color = WALL1 if cell == "W1" else WALL2
                    pygame.draw.rect(self.screen, color, self._hgap_rect(row_idx, col_idx), border_radius=r)
        for row_idx in range(BOARD_CELLS):
            for col_idx in range(BOARD_CELLS - 1):
                cell = board[row_idx * 2][col_idx * 2 + 1]
                if cell:
                    color = WALL1 if cell == "W1" else WALL2
                    pygame.draw.rect(self.screen, color, self._vgap_rect(row_idx, col_idx), border_radius=r)

    def _draw_pawn(self, board_row, board_col, color, shine_color):
        rect   = self._cell_rect(board_row // 2, board_col // 2)
        cx, cy = rect.centerx, rect.centery
        radius = self.C // 2 - max(self.C // 8, 4)
        pygame.draw.circle(self.screen, PAWN_RIM, (cx, cy + max(radius // 6, 2)), radius)
        pygame.draw.circle(self.screen, PAWN_RIM, (cx, cy), radius + 1)
        pygame.draw.circle(self.screen, color, (cx, cy), radius)
        pygame.draw.circle(self.screen, shine_color,
                           (cx - radius // 3, cy - radius // 3), max(radius // 3, 2))

    def _draw_hud(self, game_state):
        hud_y = self.M * 2 + self.board_px
        pygame.draw.rect(self.screen, HUD_BG, pygame.Rect(0, hud_y, self.W, HUD_H))

        pad = self.M
        mid = HUD_H // 2 - self.font.get_height() // 2

        turn_surf = self.font.render(f"Turn: Player {game_state.turn}", True, TEXT)
        p1_surf   = self.font.render(f"P1  {game_state.player1_walls} walls", True, PAWN1)
        p2_surf   = self.font.render(f"P2  {game_state.player2_walls} walls", True, PAWN2)

        self.screen.blit(turn_surf, (pad,               hud_y + mid))
        self.screen.blit(p1_surf,   (self.W // 3,       hud_y + mid))
        self.screen.blit(p2_surf,   (self.W * 2 // 3,   hud_y + mid))