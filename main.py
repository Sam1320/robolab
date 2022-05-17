import pygame
import pygame_menu


class MainGUI():
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((600, 400))
        self.game = None
        self.menu = pygame_menu.Menu('RoboLab', 600, 400,
                                theme=pygame_menu.themes.THEME_SOLARIZED)

        self.menu.add.text_input('Name :', default='')
        self.menu.add.selector('Game :', [('Particle Filter', 1), ('A*', 2)], default=1, onchange=self.set_game)
        # menu.add.range_slider('Grid Width :', default=10, range_values=list(range(10, 51, 10)))
        # menu.add.range_slider('Grid Height :', default=10, range_values=list(range(10, 51, 10)))

        self.menu.add.button('Play', self.start_the_game)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

    def start(self):
        self.menu.mainloop(self.surface)

    def set_game(self, value, game_num):
        self.game = value[0][0]

    def start_the_game(self, ):
        # Do the job here !
        match self.game:
            case 'A*':
                import motion_planning
                self.gui = motion_planning.MotionPlanningGUI()
            case 'Particle Filter':
                import particle_filter
                self.gui = particle_filter.ParticleFilterGUI()
        self.gui.start(verbose=True)
        self.surface = pygame.display.set_mode((600, 400))


main_gui = MainGUI()
main_gui.start()