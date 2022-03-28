from constants import *


def remove_row(board, row):
    del board[row]
    return [[0 for _ in range(config_game['cols'])]] + board


def all_values(board, boardOld):
    values = []
    cleared_rows, board = calc_rows_ret_list(board)

    values.extend(cleared_rows)
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