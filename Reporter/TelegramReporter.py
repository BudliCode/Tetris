import time

import telepot

import pygame
from neat.reporting import BaseReporter


class TelegramReporter(BaseReporter):
    def __init__(self, graphic=True, file="score.txt"):
        BaseReporter.__init__(self)
        self.graphic = graphic
        self.file = file
        self.clear_file()
        self.token = ""
        self.chat_id = ""
        self.get_token()
        self.bot = telepot.Bot(self.token)
        self.current_gen = 0
        self.best_fitness_gen = 0
        self.best_fitness = 0

    def get_token(self):
        with open("Reporter/token.txt", "r") as f:
            self.token = f.readline().strip()
            self.chat_id = f.readline().strip()

    def clear_file(self):
        with open(self.file, "w") as f:
            f.write("")

    def start_generation(self, generation):
        self.current_gen = generation

    def end_generation(self, config, population, species_set):
        best_fitness_of_gen = self.get_best_generation(species_set.species)
        self.save_best_gen_fitness(best_fitness_of_gen)
        if self.graphic:
            self.create_image()
        self.send_message(best_fitness_of_gen)

    def get_best_generation(self, species):
        all_fitness = []
        for s in species.values():
            all_fitness.append(s.fitness)
        return max(all_fitness)

    def save_best_gen_fitness(self, best_fitness):
        with open(self.file, "a") as f:
            f.write(str(best_fitness) + "\n")

    def det_best_fitness(self, best_gen_fitness):
        if best_gen_fitness > self.best_fitness:
            self.best_fitness = best_gen_fitness
            self.best_fitness_gen = self.current_gen

    def create_image(self):
        pygame.init()
        width = 1000
        height = 800
        screen = pygame.display.set_mode([width, height])
        screen.fill((0, 0, 0))
        coords = []

        with open(self.file, "r") as f:
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

    def send_message(self, record):
        message = f"Current Generation:\t{self.current_gen}\n" \
                  f"Current Fitness:\t{record}\n" \
                  f"Best Generation:\t{self.best_fitness_gen}\n" \
                  f"Best Fitness:\t{self.best_fitness}"
        try:
            if self.graphic:
                self.bot.sendPhoto(self.chat_id, photo=open("screenshot.jpg", "rb"), caption=message)
            else:
                self.bot.sendMessage(self.chat_id, message)
            # self.loop_updates()
        except ConnectionError:
            pass

    def loop_updates(self):
        updates = self.bot.getUpdates()
        for update in updates:
            print(update)
            try:
                self.bot.deleteMessage(update["message"]["message_id"])
            except Exception as e:
                print(e)
