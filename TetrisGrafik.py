from tetris import TetrisApp


class TetrisGrafik(TetrisApp):
    def __init__(self, ):
        TetrisApp.__init__()

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
                            config_game['cell_size'] + self.pos * (field_width + config_game['space']),
                            (off_y + y) *
                            config_game['cell_size'],
                            config_game['cell_size'],
                            config_game['cell_size']), 0)

    def draw_bg(self):
        pygame.draw.rect(screen,
                         (0, 0, 0), (
                             self.pos * (field_width + config_game['space']),
                             0,
                             field_width,
                             field_height),
                         0
                         )

    def draw_frame(self):
        pygame.draw.rect(screen,
                         (255, 255, 255), (
                             self.pos * (field_width + config_game['space']),
                             0,
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
            (self.pos + 1) * (field_width + config_game['space']) - msgim_center_x - 15,
            10))

    def draw_next_stones(self):
        for i in range(4):
            self.draw_matrix(self.tetris_shapes[i], (4, 18 + 3 * i))

    def draw_hold(self):
        if self.hold:
            self.draw_matrix(self.hold, (0, 17))

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