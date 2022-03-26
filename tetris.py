import random

# The configuration
config_game = {
    'cell_size': 10,
    'space': 10,
    'cols': 10,
    'rows': 20,
    'games_per_row': 5,
    'max_moves': 8000
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
    cleared_rows, board = calc_rows_ret_list(board)

    values.append(cleared_rows)
    values.append(calc_holes_diff(board, boardOld))
    values.append(calc_blocks_over_holes_diff(board, boardOld))
    values.append(calc_max_height(board))
    values.append(calc_height(board, boardOld))
    values.append(calc_height_border(board))
    values.append(calc_general_height_diff(board))
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
    value = 0
    for i, row in enumerate(board[:-1]):
        if 0 not in row:
            board = remove_row(board, i)
            rows += 1

    if rows == 1:
        value += 40
    elif rows == 2:
        value += 100
    elif rows == 3:
        value += 300
    elif rows == 4:
        value += 1200
    return value, board


def calc_rows_ret_list(board):
    rows = 0
    value = [0 for _ in range(4)]
    for i, row in enumerate(board[:-1]):
        if 0 not in row:
            board = remove_row(board, i)
            rows += 1
    value[rows - 1] = 1
    return value, board


def calc_holes(board, roof):
    holes = 0
    for x in range(config_game['cols']):
        for y in range(roof[x]):
            if not board[config_game['rows'] - y][x]:
                holes += 1
    return holes


def calc_holes_diff(board, boardOld):
    diff = calc_holes(board, calc_roof(board)) - calc_holes(boardOld, calc_roof(boardOld))
    return diff


def calc_lowest_air(board):
    floor_n_holes = [0 for _ in range(config_game['cols'])]
    for x in range(config_game['cols']):
        for y in range(config_game['rows'], 0, -1):
            if not board[y][x]:
                floor_n_holes[x] = y
                break
    return floor_n_holes


def calc_blocks_over_holes(board):
    floor_n_holes = calc_lowest_air(board)
    value = 0
    for x, i in enumerate(floor_n_holes):
        for y in range(i, 0, -1):
            if board[y][x]:
                value += 1
    return value


def calc_blocks_over_holes_diff(board, old_board):
    value_old = calc_blocks_over_holes(old_board)
    value_new = calc_blocks_over_holes(board)
    return value_new-value_old


def calc_max_height(board):
    roof = calc_roof(board)
    max_height = max(roof)
    return max_height


def calc_height(board, board_old):
    roof = calc_roof(board)
    roof_old = calc_roof(board_old)
    new_block = [0]
    heightdiff = [roof[x] - roof_old[x] for x in range(config_game['cols'])]
    for x in range(len(heightdiff)):
        if heightdiff[x]:
            new_block.append(roof[x])
    height = max(new_block)
    return height


def calc_height_border(board):
    roof = calc_roof(board)
    if roof[0] < roof[-1]:
        value = roof[0]
    else:
        value = roof[-1]
    return value


def calc_general_height_diff(board):
    value = 0
    roof = calc_roof(board)
    for i in range(len(roof)-1):
        value += abs(roof[i] - roof[i+1])
    return value


class TetrisApp(object):
    def __init__(self, max_moves):
        self.moves_left = max_moves
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
