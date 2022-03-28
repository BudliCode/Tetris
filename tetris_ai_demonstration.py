import datetime
import gzip
import pickle
import random

import neat
import pygame
import sys

# The configuration
from calc_board_values import *

config_game = {
    'cell_size': 20,
    'space': 10,
    'cols': 10,
    'rows': 20,
    'games': 2,
    'delay': 750,
    'maxfps': 30
}

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 150, 0),
    (0, 0, 255),
    (255, 120, 0),
    (255, 255, 0),
    (180, 0, 255),
    (0, 220, 220)
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


def restore_checkpoint(filename):
    with gzip.open(filename) as f:
        generation, config, population, species_set, rndstate = pickle.load(f)
        return config, population


def best_genome(population: dict):
    best_g = None
    for p in population.values():
        if best_g is None:
            best_g = p
        elif p.fitness is None:
            continue
        elif p.fitness >= best_g.fitness:
            best_g = p
    return best_g


def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for _ in range(config_game['cols'])]] + board


def join_matrices(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for _ in range(config_game['cols'])]
             for _ in range(config_game['rows'])]
    board += [[1 for _ in range(config_game['cols'])]]
    return board


class TetrisApp(object):
    def __init__(self, pos):
        self.pos = pos

        self.is_bot = False
        self.net = None
        self.start_time = datetime.datetime.now()
        self.delay = datetime.timedelta(milliseconds=200)
        self.next_moves = []

        self.isAlive = True
        self.score = 0
        self.board = new_board()
        self.tetris_shapes = []
        self.stone = None
        self.stone_x = None
        self.stone_y = None
        self.hold = None
        self.new_stone()

    def new_stone(self):
        while len(self.tetris_shapes) <= 6:
            self.tetris_shapes.extend(random.sample(tetris_shapes, len(tetris_shapes)))
        self.stone = self.tetris_shapes.pop(0)
        self.stone_x = int(config_game['cols'] / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.isAlive = False
        if self.is_bot:
            self.calc_move()

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

    def move(self, delta_x):
        if self.isAlive:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > config_game['cols'] - len(self.stone[0]):
                new_x = config_game['cols'] - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def drop(self):
        if self.isAlive:
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrices(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                self.new_stone()
                self.calc_score()

    def drop_down(self):
        if self.isAlive:
            while True:
                self.stone_y += 1
                if check_collision(self.board,
                                   self.stone,
                                   (self.stone_x, self.stone_y)):
                    self.board = join_matrices(
                        self.board,
                        self.stone,
                        (self.stone_x, self.stone_y))
                    self.new_stone()
                    self.calc_score()
                    return

    def rotate_stone(self):
        if self.isAlive:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def switch_hold(self):
        if self.hold:
            temp_hold = self.hold
            self.hold = self.stone
            self.stone = temp_hold
            self.stone_y = 0
            self.stone_x = int(config_game['cols'] / 2 - len(self.stone[0]) / 2)
        else:
            self.hold = self.stone
            self.new_stone()

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
                             config_game['rows'] * config_game['cell_size']),
                         1
                         )

    def calc_score(self):
        c = 0
        for i, row in enumerate(self.board[:-1]):
            if 0 not in row:
                self.board = remove_row(
                    self.board, i)
                c += 1

        if c == 1:
            self.score += 40
        elif c == 2:
            self.score += 100
        elif c == 3:
            self.score += 300
        elif c == 4:
            self.score += 1200
        elif c > 4:
            print("Overscore:", c)

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
        if self.is_bot:
            self.make_move()

    def make_move(self):
        current_time = datetime.datetime.now()
        if current_time - self.start_time > self.delay:
            self.next_move()
            self.start_time = current_time

    def next_move(self):
        mv = self.next_moves.pop(0)
        if mv == "rot":
            self.rotate_stone()
        elif mv == "left":
            self.move(-1)
        elif mv == "right":
            self.move(1)
        elif mv == "dropdown":
            self.drop_down()

    def calc_move(self):
        all_possibilities = []
        all_possibilities.extend(self.calc_all_possibilities(self.stone, net, 0))
        if self.hold:
            all_possibilities.extend(self.calc_all_possibilities(self.hold, net, 1))
        else:
            all_possibilities.extend(self.calc_all_possibilities(self.tetris_shapes[0], net, 1))
        best_move = self.get_best_move(all_possibilities)
        # print(best_move)
        if best_move[3]:
            self.switch_hold()
        self.next_moves = []
        for i in range(best_move[1]):
            self.next_moves.append("rot")
        if best_move[2] - self.stone_x < 0:
            for i in range(abs(best_move[2] - self.stone_x)):
                self.next_moves.append("left")
        if best_move[2] - self.stone_x > 0:
            for i in range(abs(best_move[2] - self.stone_x)):
                self.next_moves.append("right")
        self.next_moves.append("dropdown")

    def get_best_move(self, all_possibilities):
        bm = all_possibilities[0]
        for p in all_possibilities:
            if p[0] > bm[0]:
                bm = p[:]
        return bm

    def calc_all_possibilities(self, stone, net, is_hold):
        all_possibilities = []
        for rotations in range(4):
            for location in range(config_game['cols']):
                stone_y = 0
                while True:
                    if check_collision(self.board, stone, (location, stone_y)):
                        stone_y -= 1
                        break
                    stone_y += 1
                if stone_y < 0:
                    continue
                temp_board = join_matrices(copy_board(self.board), stone, (location, stone_y))
                values = all_values(temp_board, copy_board(self.board))
                all_possibilities.append([net.activate(values)[0], rotations, location, is_hold])
                # all_possibilities.append([random.random(), i, j, is_hold])
            stone = rotate_clockwise(stone)
        return all_possibilities


def manual():
    player = 0
    tetri = [TetrisApp(t) for t in range(2)]
    tetri[1].is_bot = True
    tetri[1].net = net
    tetri[1].new_stone()
    dont_burn_my_cpu = pygame.time.Clock()
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                for tetris in tetri:
                    tetris.drop()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tetri[player].move(-1)
                elif event.key == pygame.K_RIGHT:
                    tetri[player].move(1)
                elif event.key == pygame.K_UP:
                    tetri[player].rotate_stone()
                elif event.key == pygame.K_h:
                    tetri[player].switch_hold()
                elif event.key == pygame.K_DOWN:
                    tetri[player].drop()
                elif event.key == pygame.K_SPACE:
                    tetri[player].drop_down()

        for i, tetris in enumerate(tetri):
            if not tetris.isAlive:
                continue
            tetris.update()
        pygame.display.update()
        dont_burn_my_cpu.tick(config_game['maxfps'])


if __name__ == '__main__':
    pygame.init()
    pygame.key.set_repeat(250, 25)

    field_width = config_game['cell_size'] * config_game['cols']
    field_height = config_game['cell_size'] * (config_game['rows'] + 14)
    width = field_width * config_game['games'] + config_game['space'] * (config_game['games']-1)
    height = field_height

    screen = pygame.display.set_mode((width, height))
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    pygame.time.set_timer(pygame.USEREVENT + 1, config_game['delay'])

    config, pop = restore_checkpoint("neat-checkpoint-106")
    genome = best_genome(pop)
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    manual()
