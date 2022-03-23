import os
from PIL import Image, ImageDraw
import pygame
import telepot
from neat.reporting import BaseReporter


def get_token():
    with open("Reporter/token.txt", "r") as f:
        token = f.readline().strip()
        chat_id = f.readline().strip()
    return token, chat_id


def clear_file(file):
    with open(file, "w") as f:
        f.write("")


def get_best_fitness_of_gen(species_set):
    value = 0
    for s in species_set.species.values():
        if s.fitness and s.fitness > value:
            value = s.fitness
    return value


def add_score(file, score):
    with open(file, "a") as f:
        f.write(str(score) + "\n")


def det_best_fitness(former_gen_values, current_gen_values):
    if current_gen_values[1] > former_gen_values[1]:
        return current_gen_values
    return former_gen_values


def get_average_fitness(file):
    total_value = 0
    all_values = 1
    with open(file, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            total_value += int(line.strip())
            all_values = i + 1
    return total_value / all_values


def create_image_pillow(file):
    mode = 'RGB'
    width = 1000
    height = 800
    black = (0, 0, 0)
    white = (255, 255, 255)
    l_width = 1
    img = Image.new(mode, (width, height), black)
    draw = ImageDraw.Draw(img)
    coords = []

    with open(file, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            coords.append([i, int(line.strip())])

    heights = []
    for c in coords:
        heights.append(c[1])
    highest_value = max(heights)

    for i, c in enumerate(coords):
        if i < len(coords) - 1:
            x1 = c[0] * width / len(coords)
            y1 = height - c[1] * height / (highest_value + 1000)
            x2 = coords[i + 1][0] * width / len(coords)
            y2 = height - coords[i + 1][1] * height / (highest_value + 1000)
            draw.line((x1, y1, x2, y2), fill=white, width=l_width)
    img.save("screenshot.jpg")


def create_image(file):
    pygame.init()
    width = 1000
    height = 800
    screen = pygame.display.set_mode([width, height])
    screen.fill((0, 0, 0))
    coords = []

    with open(file, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            coords.append([i, int(line.strip())])

    heights = []
    for c in coords:
        heights.append(c[1])
    highest_value = max(heights)

    for i, c in enumerate(coords):
        if i < len(coords) - 1:
            x1 = c[0] * width / len(coords)
            y1 = height - c[1] * height / (highest_value + 1000)
            x2 = coords[i + 1][0] * width / len(coords)
            y2 = height - coords[i + 1][1] * height / (highest_value + 1000)
            pygame.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2))
    pygame.display.update()
    pygame.image.save(screen, "screenshot.jpg")
    pygame.quit()


def create_message(info):
    message = f"Current Generation:\t{info[0]}\n" \
              f"Current Fitness:\t{info[1]}\n" \
              f"Best Generation:\t{info[2]}\n" \
              f"Best Fitness:\t{info[3]}\n" \
              f"Average Fitness:\t{info[4]:.2f}"
    return message


class TelegramMessageHandler:
    def __init__(self, grafisch):
        self.last_message_id = None
        self.token, self.chat_id = get_token()
        self.grafisch = grafisch

    def send_message(self, message):
        bot = telepot.Bot(self.token)
        if self.last_message_id:
            bot.deleteMessage((self.chat_id, self.last_message_id))
        if self.grafisch:
            message_info = bot.sendPhoto(self.chat_id,open("screenshot.jpg", "rb"), message)
        else:
            message_info = bot.sendMessage(self.chat_id, message)
        self.last_message_id = message_info["message_id"]


class TelegramReporter(BaseReporter):
    def __init__(self, graphic=True, file="score.txt"):
        BaseReporter.__init__(self)
        self.graphic = graphic
        self.score_file = file
        self.current_gen = 0
        self.best_fitness = [0, 0]
        self.message_handler = TelegramMessageHandler(graphic)

    def start_generation(self, generation):
        self.current_gen = generation
        if self.current_gen == 0:
            clear_file(self.score_file)

    def end_generation(self, config, population, species_set):
        best_fitness_of_gen = get_best_fitness_of_gen(species_set)
        add_score(self.score_file, best_fitness_of_gen)
        self.best_fitness = det_best_fitness(self.best_fitness, (self.current_gen, best_fitness_of_gen))
        average_fitness = get_average_fitness(self.score_file)
        message = create_message((
            self.current_gen,
            best_fitness_of_gen,
            self.best_fitness[0],
            self.best_fitness[1],
            average_fitness
        ))
        if self.graphic:
            create_image_pillow(self.score_file)
            self.message_handler.send_message(message)
            os.remove("screenshot.jpg")
        else:
            self.message_handler.send_message(message)
