import datetime
import os
import sys

from neat import Checkpointer

from Reporter.TelegramReporter import TelegramReporter
import neat
import pygame


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

    pop = neat.Population(config)
    # pop = neat.Checkpointer.restore_checkpoint("neat-checkpoint-13")
    # pop.add_reporter(neat.StdOutReporter(True))
    # stats = neat.StatisticsReporter()
    # pop.add_reporter(stats)
    checkpoint = Checkpointer(generation_interval=10)
    pop.add_reporter(checkpoint)
    tele = TelegramReporter(True)
    pop.add_reporter(tele)
    winner = pop.run(eval_genomes, 10000)
    # visualize.draw_net(config, winner, True, node_names=node_names)
    # visualize.plot_stats(stats, ylog=False, view=True)
    # visualize.plot_species(stats, view=True)


if __name__ == '__main__':

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    Grafisch = False

    from tetris import config_game
    if Grafisch:
        from TetrisGrafik import TetrisGrafik as TetrisApp, screen
    else:
        from tetris import TetrisApp

    run(config_path)
