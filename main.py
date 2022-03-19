


if __name__ == '__main__':
    pygame.init()
    pygame.key.set_repeat(250, 25)

    field_width = config_game['cell_size'] * config_game['cols']
    field_height = config_game['cell_size'] * config_game['rows'] * 2
    width = field_width * config_game['games'] + config_game['space'] * (config_game['games']-1)
    height = field_height

    screen = pygame.display.set_mode((width, height))
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    pygame.time.set_timer(pygame.USEREVENT + 1, config_game['delay'])

    manual()
