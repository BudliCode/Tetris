import os
import random
import sys
import time
import neat
import pygame

# from Dinosaur import visualize

config_game = {
    'cell_size': 20,
    'cols': 8,
    'rows': 16,
    'delay': 50,
    'act': 25,
    'maxfps': 300
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
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for _ in range(config_game['cols'])]] + board


def join_matrices(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            if val != 0:
                mat1[cy + off_y - 1][cx + off_x] = val
    return mat1


def new_board():
    board = [[0 for _ in range(config_game['cols'])]
             for _ in range(config_game['rows'])]
    board += [[1 for _ in range(config_game['cols'])]]
    return board


class Neurons:
    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.hidden = {}
        self.lines = []

    def add_input(self, name):
        self.inputs.append(name)

    def add_output(self, name):
        self.outputs.append(name)

    def add_hidden(self, n):
        self.hidden[n] = [0]

    def add_line(self, a, b, param):
        self.lines.append([a, b, param])
        if b in self.hidden.keys():
            self.hidden[b].append(a)

    def calc_values(self):
        for k in self.hidden.keys():
            value = self.recourse_chain_value(self.hidden.get(k)[1:])
            self.hidden[k][0] = value

    def recourse_chain_value(self, d):
        values = [0]
        for k in d:
            if int(k) > 0:
                if int(k) <= 3:
                    continue
                try:
                    values.append(self.recourse_chain_value(self.hidden.get(k)[1:]) + 1)
                except ValueError:
                    raise
            else:
                values.append(1)

        return max(values)

    def calc_max_value(self):
        values = [0]
        for k in self.hidden.keys():
            value = self.hidden.get(k)[0]
            values.append(value)
        return max(values)

    def sort_hidden_values(self, max_value):
        sorted_values = [[] for _ in range(max_value)]
        for k in self.hidden.keys():
            sorted_values[self.hidden.get(k)[0]-1].append(k)
        return sorted_values

    def calc_d_x(self, sorted_values):
        d_x = []
        for s in sorted_values:
            d_x.append(len(s))
        return d_x

    def calc_coords(self, pos):
        self.calc_values()
        max_value = self.calc_max_value()
        sorted_values = self.sort_hidden_values(max_value)
        d_x = self.calc_d_x(sorted_values)
        i_y = 50
        o_y = 250
        d_y = (o_y - i_y) / (max_value + 1)
        input_pos = []
        x_init = pos[0] * (160 + 10)
        y_init = 320
        space = 160 / (len(self.inputs) + 1)
        for i in range(len(self.inputs)):
            x = x_init + (i + 1) * space
            y = y_init + 50
            input_pos.append((x, y))

        output_pos = []
        space = 160 / (len(self.outputs) + 1)
        for i in range(len(self.outputs)):
            x = x_init + (i + 1) * space
            y = y_init + 250
            output_pos.append((x, y))

        hidden_pos = []
        for i, k in enumerate(sorted_values):
            space = 160 / (len(k) + 1)
            for j, l in enumerate(k):
                x = x_init + (j + 1) * space
                y = y_init + i_y + d_y * (i + 1)
                hidden_pos.append((x, y))

        input_dict = dict(zip(self.inputs, input_pos))
        output_dict = dict(zip(self.outputs, output_pos))
        hidden_dict = dict(zip(self.hidden, hidden_pos))
        output_dict.update(hidden_dict)
        input_dict.update(output_dict)

        return input_dict

    def render(self, pos):
        vals = self.calc_coords(pos)

        colors_line = {'green': (0, 255, 0),
                       'red': (255, 0, 0),
                       'blue': (0, 0, 255)}
        for i in self.lines:
            x1 = vals.get(i[0])[0]
            y1 = vals.get(i[0])[1]
            x2 = vals.get(i[1])[0]
            y2 = vals.get(i[1])[1]
            col = colors_line.get(i[2].get("color"))
            width = float(i[2].get("penwidth"))
            try:
                pygame.draw.line(screen,
                                 [f * width for f in col],
                                 (x1, y1),
                                 (x2, y2),
                                 2)
            except ValueError:
                print(width)
                print(f * width for f in col)
                raise
        for i in vals.values():
            x = i[0]
            y = i[1]
            pygame.draw.circle(screen,
                               (255, 255, 255),
                               (x, y),
                               5, 0)
            pygame.draw.circle(screen,
                               (0, 0, 0),
                               (x, y),
                               5, 2)


def render_net(config, genome, pos):
    dot = Neurons()
    inputs = set()
    for k in config.genome_config.input_keys:
        inputs.add(k)
        name = node_names.get(k, str(k))
        dot.add_input(name)

    outputs = set()
    for k in config.genome_config.output_keys:
        outputs.add(k)
        name = node_names.get(k, str(k))
        dot.add_output(name)

    used_nodes = set(genome.nodes.keys())
    for n in used_nodes:
        if n in inputs or n in outputs:
            continue
        dot.add_hidden(str(n))

    for cg in genome.connections.values():
        if cg.enabled:
            inp, output = cg.key
            a = node_names.get(inp, str(inp))
            b = node_names.get(output, str(output))
            color = 'green' if cg.weight > 0 else 'red'
            width = str(0.1 + abs(cg.weight / 5.0))
            dot.add_line(a, b, {'color': color, 'penwidth': width})

    dot.render(pos)


class TetrisApp:
    def __init__(self, pos):
        self.pos = pos
        self.width = config_game['cell_size'] * config_game['cols']
        self.height = config_game['cell_size'] * config_game['rows']
        self.isAlive = True
        self.score = 0
        self.board = new_board()
        self.new_stone()

    def new_stone(self):
        self.rotation = 0
        self.stone_num = random.randrange(len(tetris_shapes))
        self.stone = tetris_shapes[self.stone_num]
        self.stone_x = int(config_game['cols'] / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.isAlive = False

    def draw_score(self):
        msg_image = pygame.font.Font(
            pygame.font.get_default_font(), 12).render(
            str(self.score), False, (255, 255, 255), (0, 0, 0))

        msgim_center_x, msgim_center_y = msg_image.get_size()

        screen.blit(msg_image, (
            (self.pos[0] + 1) * 170 - msgim_center_x - 15,
            self.pos[1] * 370 + 10))

    def draw_frame(self):
        pygame.draw.rect(screen,
                         (255, 255, 255), (
                             self.pos[0] * 170,
                             self.pos[1] * 170,
                             160,
                             320),
                         1
                         )

    def draw_bg(self):
        pygame.draw.rect(screen,
                         (0, 0, 0), (
                             self.pos[0] * 170,
                             self.pos[1] * 170,
                             170,
                             320),
                         0
                         )

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
                            config_game['cell_size'] + self.pos[0] * 170,
                            (off_y + y) *
                            config_game['cell_size'] + self.pos[1],
                            config_game['cell_size'],
                            config_game['cell_size']), 0)

    def move(self, delta_x):
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
        self.stone_y += 1
        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.board = join_matrices(
                self.board,
                self.stone,
                (self.stone_x, self.stone_y))
            self.new_stone()

    def rotate_stone(self):
        if self.isAlive:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone
                self.rotation += 1
                if self.rotation == 4:
                    self.rotation = 0

    def set_values(self, d, u, x):
        if d > 0.5:
            self.drop()
        if u > 0.5:
            self.rotate_stone()
        if x < 0.3:
            self.move(-1)
        elif x > 0.3:
            self.move(1)

    def calc_row_values(self):
        v = []
        for x in range(config_game["cols"]):
            no_col = True
            h = 16
            holes = 0
            for y in range(config_game["rows"]):
                if self.board[y][self.stone_x] == 1:
                    no_col = False
                else:
                    if not no_col:
                        holes += 1
                if no_col:
                    h -= 1
            v.append(h)
            v.append(holes)
        return v

    def get_values(self):
        values = {"Stone": self.stone_num, "Rot": self.rotation, "x": self.stone_x, "y": self.stone_y}
        board = self.calc_row_values()
        return values, board

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

    def update(self):
        self.draw_bg()
        self.draw_matrix(self.board, (0, 0))
        self.draw_matrix(self.stone,
                         (self.stone_x,
                          self.stone_y))
        self.draw_score()
        self.calc_score()
        self.draw_frame()


def tetris_test():
    clock = pygame.time.Clock()
    pygame.key.set_repeat(250, 25)

    tetri = []
    am = 3
    for i in range(am + 1):
        tetri.append(TetrisApp((i % 4, i // 4)))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT + 1:
                for tetris in tetri:
                    if not tetris.isAlive:
                        continue
                    tetris.drop()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    tetri[am].rotate_stone()
                elif event.key == pygame.K_DOWN:
                    tetri[am].drop()
                elif event.key == pygame.K_LEFT:
                    tetri[am].move(-1)
                elif event.key == pygame.K_RIGHT:
                    tetri[am].move(1)

        for i, tetris in enumerate(tetri):
            if not tetris.isAlive:
                continue
            tetris.update()
        pygame.display.update()
        clock.tick(30)
        if len(tetri) == 0:
            break


def eval_genomes(genomes, config):
    tetri = []
    ge = []
    nets = []
    clock = pygame.time.Clock()
    screen.fill((0, 0, 0))

    for i, (genome_id, genome) in enumerate(genomes):
        pos = (i % 5, i // 5)
        tetri.append(TetrisApp(pos))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

        # render_net(config, genome, pos)

    start_time = time.time()

    while True:
        drop = False
        mv = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT + 1:
                drop = True
            if event.type == pygame.USEREVENT + 2:
                mv = True

        for i, tetris in enumerate(tetri):
            if not tetris.isAlive:
                # ge[i].fitness = (time.time() - start_time) * (tetris.score + 1)
                ge[i].fitness = len(list(ge[i].nodes.keys()))
                # print(i, "died:", ge[i].fitness)
                tetri.pop(i)
                ge.pop(i)
                nets.pop(i)
                continue
            if drop:
                tetris.drop()
            if mv:
                v, b = tetris.get_values()
                output = nets[i].activate((*v.values(), *b))
                tetris.set_values(*output[:3])
            tetris.update()

        if len(tetri) == 0:
            break

        pygame.display.update()
        clock.tick(30)


def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    # pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    checkpoint = neat.Checkpointer()
    pop.add_reporter(checkpoint)
    winner = pop.run(eval_genomes, 100)
    # visualize.draw_net(config, winner, True, node_names=node_names)
    # visualize.plot_stats(stats, ylog=False, view=True)
    # visualize.plot_species(stats, view=True)


if __name__ == "__main__":
    pygame.init()
    single_width = config_game['cell_size'] * config_game['cols']
    single_height = config_game['cell_size'] * config_game['rows']
    screen_width = (config_game['cell_size'] * config_game['cols'] + 10) * 5 - 10
    screen_height = config_game['cell_size'] * config_game['rows'] * 2
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.time.set_timer(pygame.USEREVENT + 1, config_game['delay'])
    pygame.time.set_timer(pygame.USEREVENT + 2, config_game['act'])

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    node_names = {}
    node_colors = {}

    # tetris_test()
    run(config_path)
