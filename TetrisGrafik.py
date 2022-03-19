import pygame

from tetris import TetrisApp, config_game, colors


class TetrisGrafik(TetrisApp):
    def __init__(self, pos):
        TetrisApp.__init__(self)
        self.pos = pos

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            if y == config_game['rows']:
                continue
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        screen,
                        colors[val],
                        pygame.Rect(
                            (off_x + x) *
                            config_game['cell_size'] + self.pos[0] * (field_width + config_game['space']),
                            (off_y + y) *
                            config_game['cell_size'] + self.pos[1] * (config_game['rows'] + 14),
                            config_game['cell_size'],
                            config_game['cell_size']), 0)

    def draw_bg(self):
        pygame.draw.rect(screen,
                         (0, 0, 0), (
                             self.pos[0] * (field_width + config_game['space']),
                             self.pos[1] * field_height,
                             field_width,
                             field_height),
                         0
                         )

    def draw_frame(self):
        pygame.draw.rect(screen,
                         (255, 255, 255), (
                             self.pos[0] * (field_width + config_game['space']),
                             self.pos[1] * field_height,
                             field_width,
                             field_height / 2),
                         1
                         )

    def draw_score(self):
        msg_image = pygame.font.Font(
            pygame.font.get_default_font(), 12).render(
            str(self.score), False, (255, 255, 255), (0, 0, 0))

        msgim_center_x, msgim_center_y = msg_image.get_size()

        screen.blit(msg_image, (
            (self.pos[0] + 1) * (field_width + config_game['space']) - msgim_center_x - 15,
            self.pos[1] * field_height + 10))

    def draw_next_stones(self):
        for i in range(4):
            self.draw_matrix(self.tetris_shapes[i], (4, config_game['rows'] + 2 + 3 * i))

    def draw_hold(self):
        if self.hold:
            self.draw_matrix(self.hold, (0, config_game['rows'] + 1))

    def update(self):
        self.draw_bg()
        self.draw_matrix(self.board, (0, 0))
        self.draw_matrix(self.stone,
                         (self.stone_x,
                          self.stone_y))
        self.draw_hold()
        self.draw_next_stones()
        self.draw_frame()
        self.draw_score()


field_width = config_game['cell_size'] * config_game['cols']
field_height = config_game['cell_size'] * (config_game['rows'] + 14)

width = field_width * config_game['games_per_row'] + config_game['space'] * (config_game['games_per_row'] - 1)
height = field_height * 2
pygame.init()

screen = pygame.display.set_mode((width, height))