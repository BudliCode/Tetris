import random

# The configuration
config_game = {
    'cell_size': 10,
    'space': 10,
    'cols': 10,
    'rows': 20,
    'games_per_row': 5,
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


def all_values(board, boardOld):
    values = []
    cleared_rows, board = calc_rows(board)
    roof = calc_roof(board)
    roofOld = calc_roof(boardOld)

    values.append(cleared_rows)
    values.append(calc_holes_diff(board, boardOld, roof))
    values.append(calc_maxHeight(roof, ))
    values.append(calc_height(roof, roofOld))
    return values


def calc_roof(board):
    roof = []
    for x in range(config_game['cols']):
        for y in range(config_game['rows'] + 1):
            if board[y][x]:
                roof.append((config_game['rows']) - y)
                break
    return roof


def calc_rows(board):
    rows = 0
    for i, row in enumerate(board[:-1]):
        if 0 not in row:
            board = remove_row(board, i)
            rows += 1
    return rows, board


def calc_holes(board, roof):
    holes = 0
    for x in range(config_game['cols']):
        for y in range(roof[x]):
            if not board[config_game['rows'] - y][x]:
                holes += 1
    return holes


def calc_holes_diff(board, boardOld, roof):
    diff = calc_holes(board, roof) - calc_holes(boardOld, roof)
    return diff


def calc_maxHeight(roof):
    maxHeight = max(roof)
    return maxHeight


def calc_height(roof, roofOld):
    newBlock = [0]
    heightdiff = [roof[x] - roofOld[x] for x in range(config_game['cols'])]
    for x in range(len(heightdiff)):
        if heightdiff[x]:
            newBlock.append(roof[x])
    height = max(newBlock)
    return height


class TetrisApp(object):
    def __init__(self):
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
            self.score += 1200
        elif c > 4:
            print("Overscore:", c)

    def calc_move(self, net):
        all_possibilities = []
        all_possibilities.extend(self.calc_all_possibilities(self.stone, net, 0))
        if self.hold:
            all_possibilities.extend(self.calc_all_possibilities(self.hold, net, 1))
        else:
            all_possibilities.extend(self.calc_all_possibilities(self.tetris_shapes[0], net, 1))
        best_move = max(all_possibilities)
        if best_move[3]:
            self.switch_hold()
        print(best_move[1])
        for i in range(best_move[1]):
            self.rotate_stone()
        self.move(best_move[2] - self.stone_x)
        self.drop_down()

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
            rotate_clockwise(stone)
        return all_possibilities
