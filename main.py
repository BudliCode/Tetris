import os
import sys

from neat import Checkpointer

from Reporter.TelegramReporter import TelegramReporter
import neat
import pygame


def get_last_checkpoint():
    directory = os.path.dirname(os.path.abspath(__file__))

    check_points = []
    for file in os.listdir(directory):
        filename = str(os.fsdecode(file)).split("-")
        if filename[:2] == ['neat', 'checkpoint']:
            check_points.append(int(filename[2]))
    if len(check_points) == 0:
        return None
    return "-".join(("neat", "checkpoint", str(max(check_points))))


def eval_genomes(genomes, config):
    tetri = []  # Alle Tetrisspiele, die parallel laufen
    ge = []  # Speicherort für die Genomes
    nets = []  # Speicherort für die Netze
    if Grafisch:
        screen.fill((0, 0, 0))  # Schwärzt Bildschirm zu Beginn

    # Füllt die Listen mit den Spielen und Genomen
    for i, (genome_id, genome) in enumerate(genomes):
        if Grafisch:
            pos = (i % config_game['games_per_row'], i // config_game['games_per_row'])
            tetri.append(TetrisApp(pos, config_game['max_moves']))
        else:
            tetri.append(TetrisApp(config_game['max_moves']))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    while True:
        if Grafisch:
            # pygame.time.wait(500)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        # Geht die Tetri durch
        for i, tetris in enumerate(tetri):
            if tetris.moves_left <= 0:
                tetris.isAlive = False
            if not tetris.isAlive:
                # ge[i].fitness = (time.time() - start_time) * (tetris.score + 1)
                ge[i].fitness = tetris.tetrisse
                # print(i, "died:", ge[i].fitness)
                tetri.pop(i)
                ge.pop(i)
                nets.pop(i)
                continue
            # Falls Zeit zum Drop abgelaufen ist, wird Teil 1 nach unten bewegt
            tetris.calc_move(nets[i])
            if Grafisch:
                tetris.update()

        if len(tetri) == 0:
            break


def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    directory = get_last_checkpoint()

    if directory:
        pop = neat.Checkpointer.restore_checkpoint(directory)
    else:
        pop = neat.Population(config)

    checkpoint = Checkpointer(generation_interval=10)
    pop.add_reporter(checkpoint)
    # Die nächsten zwei Zeilen auskommentieren, um den TelegramBot zu deaktivieren
    tele = TelegramReporter()
    pop.add_reporter(tele)
    pop.run(eval_genomes, 10000)


if __name__ == '__main__':

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    # Möglichkeit die grafische Benutzeroberfläche zu deaktivieren, um die Performance zu steigern
    Grafisch = False

    from tetris import config_game

    if Grafisch:
        from TetrisGrafik import TetrisGrafik as TetrisApp, screen
    else:
        from tetris import TetrisApp

    run(config_path)
