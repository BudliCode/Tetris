import random

# The configuration
from calc_board_values import all_values
from constants import *


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


def copy_board(old_board):
    new_board = []
    for r in old_board:
        columns = []
        for c in r:
            columns.append(c)
        new_board.append(columns)
    return new_board


class TetrisApp(object):
    def __init__(self, max_moves):
        self.moves_left = max_moves
        self.isAlive = True
        self.score = 0
        self.tetrisse = 0
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
        else:
            self.hold = self.stone
            self.new_stone()

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
            self.tetrisse += 1200
            self.score += 1200
        elif c > 4:
            print("Overscore:", c)
        self.moves_left -= 1

    def calc_move(self, net):
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
        for i in range(best_move[1]):
            self.rotate_stone()
        self.move(best_move[2] - self.stone_x)
        self.drop_down()

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
