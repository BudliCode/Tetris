from tetris import config_game
board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 0, 5, 0, 0, 0], [0, 0, 0, 1, 5, 5, 5, 0, 0, 0], [0, 0, 0, 0, 0, 6, 6, 6, 6, 0], [0, 0, 0, 0, 0, 7, 7, 0, 0, 0], [0, 0, 0, 0, 0, 7, 7, 0, 0, 0], [0, 0, 0, 0, 0, 2, 2, 0, 0, 0], [0, 0, 0, 0, 2, 2, 0, 0, 0, 0], [0, 0, 0, 0, 4, 0, 0, 0, 0, 0], [0, 1, 1, 1, 4, 4, 4, 0, 0, 0], [0, 0, 1, 3, 3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 3, 3, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]



def calc_roof(board):
    roof = []
    for x in range(config_game['cols']):
        for y in range(config_game['rows']+1):
            if board[y][x]:
                l.append((config_game['rows'])-y)
                break
    return roof