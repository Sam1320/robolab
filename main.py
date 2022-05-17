import pygame
import pygame_menu
import motion_planning
import particle_filter


class AStarMenu(pygame_menu.Menu):
    def __init__(self, name, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, width, height, theme=theme)
        self.add.range_slider('Grid Width :', default=10, range_values=list(range(10, 51, 10)))
        self.add.range_slider('Grid Height :', default=10, range_values=list(range(10, 51, 10)))
        self.add.button('Ok', self.start_the_game)

    def start(self, surface):
        self.mainloop(surface)

    def start_the_game(self):
        self.gui = motion_planning.MotionPlanningGUI()
        self.gui.start()
        pygame.display.set_mode((600, 400))


class ParticleMenu(pygame_menu.Menu):
    def __init__(self, name, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, width, height, theme=theme)
        self.add.range_slider('Number of Particles:', default=200, range_values=[10, 100, 200, 400, 800], onchange=self.set_number_of_particles)
        self.add.button('Ok', self.start_the_game)
        self.number_of_particles = 200

    def start(self, surface):
        self.mainloop(surface)

    def set_number_of_particles(self, value):
        self.number_of_particles = value

    def start_the_game(self):
        self.gui = particle_filter.ParticleFilterGUI(n_particles=self.number_of_particles)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class MainGUI():
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((600, 400))
        self.game = None
        self.menu = pygame_menu.Menu('RoboLab', 600, 400,
                                theme=pygame_menu.themes.THEME_SOLARIZED)

        self.menu.add.text_input('Name :', default='')
        self.menu.add.selector('Game :', [('Particle Filter', 1), ('A*', 2)], default=1, onchange=self.set_game)

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
                self.menu = AStarMenu('A* Settings')
            case 'Particle Filter':
                self.menu = ParticleMenu('Particle Filter Settings')
        self.menu.start(self.surface)
        self.surface = pygame.display.set_mode((600, 400))


main_gui = MainGUI()
main_gui.start()