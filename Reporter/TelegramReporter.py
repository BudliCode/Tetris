from neat.reporting import BaseReporter


class TelegramReporter(BaseReporter):
    def __init__(self, file="score.txt"):
        BaseReporter.__init__(self)
        self.current_gen = 0
        self.file = file
        self.clear_file()

    def clear_file(self):
        with open(self.file) as f:
            f.write("")

    def start_generation(self, generation):
        self.current_gen = generation

    def end_generation(self, config, population, species_set):
        pass

    def get_best_generation(self, species_set):
        pass

    def save_best_fitness(self):
        pass

    def send_message(self):
        pass
