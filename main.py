import os

import pygame
import pygame_menu

import datatypes
import env
import kalman_filter_1d
import kalman_filter_2d
import motion_planning
import particle_filter

#TODO:
# improve buttons positions
# implement start_the_game() in base class GameMenu

# DONE add explanation window

#Ideas:
# Add "about" section in main window explaining the motivation and some details of the gui
# Add option to automatically perform measurement update when moving (kalman filter 2d)


class GameMenu(pygame_menu.Menu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, width, height, theme=theme, onclose=pygame_menu.events.BACK)
        self.add.button('Controls', self.controls)
        self.add.button('Settings', self.settings)
        self.add.button('Play', self.start_the_game)
        self.add.button('Back', self.go_back)
        self.surface = surface
        self.gui_class = datatypes.RobotGUI

    def controls(self):
        pass

    def settings(self):
        pass

    def go_back(self):
        self.close()

    def start(self):
        self.mainloop(self.surface)

    def start_the_game(self):
        pass
    #     self.gui = self.gui_class()
    #     self.gui.start()
    #     pygame.display.set_mode((600, 400))


class AStarMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, surface, width, height, theme=theme)
        self.width = 10
        self.height = 10
        self.surface = surface
        self.load_map = 0
        self.obstacle_prob = 0.2

    def controls(self):
        menu = pygame_menu.Menu('A* Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()
        table.add_row(['Left click', 'set star position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Right click', 'set goal position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Middle click', 'modify map'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        table.add_row(['Enter', 'save map'], cell_padding=8, cell_font_size=20)

        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def settings(self):
        menu = pygame_menu.Menu('A* Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.toggle_switch('Load Map', default=self.load_map, onchange=self.set_map_load)
        menu.add.range_slider('Obstacle Probability:', default=self.obstacle_prob, range_values=[0, 0.2, 0.4, 0.6, 0.8, 1], onchange=self.set_obstacle_prob)
        menu.add.range_slider('Grid Width :', default=self.width, range_values=list(range(10, 51, 10)), onchange=self.set_width)
        menu.add.range_slider('Grid Height :', default=self.height, range_values=list(range(10, 51, 10)), onchange=self.set_height)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def set_obstacle_prob(self, value):
        self.obstacle_prob = value

    def set_map_load(self, value):
        self.load_map = value

    def set_width(self, value):
        self.width = value

    def set_height(self, value):
        self.height = value

    def start_the_game(self):
        self.gui = motion_planning.MotionPlanningGUI(world_size=(self.width, self.height), load_grid=self.load_map, obstacle_prob=self.obstacle_prob)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class ParticleMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, surface, width, height, theme=theme)

        self.number_of_particles = 200
        self.forward_noise = 0.05
        self.turning_noise = 0.05
        self.sense_noise = 5
        self.gui = None

    def controls(self):
        menu = pygame_menu.Menu('Particle Filter Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)

        table = menu.add.table()
        table.add_row(['Up arrow', 'Move forward'], cell_padding=8, cell_font_size=20)
        table.add_row(['Right arrow', 'Turn rightward'], cell_padding=8, cell_font_size=20)
        table.add_row(['Down arrow', 'Move backward'], cell_padding=8, cell_font_size=20)
        table.add_row(['Left arrow', 'Turn leftward'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        table.add_row(['Enter', 'save map'], cell_padding=8, cell_font_size=20)

        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def settings(self):
        menu = pygame_menu.Menu('Particle Filter Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.vertical_margin(25)
        menu.add.range_slider('Number of Particles:', default=self.number_of_particles, range_values=[10, 100, 200, 400, 800], onchange=self.set_number_of_particles)
        menu.add.range_slider('Number of Planets:', default=2, range_values=(1, 7), increment=1, onchange=self.set_number_of_particles)
        menu.add.range_slider('Forward noise:', default=self.forward_noise, range_values=(0, 5),increment=0.05, onchange=self.set_forward_noise)
        menu.add.range_slider('Turing noise:', default=self.turning_noise, range_values=(0, 5),increment=0.05, onchange=self.set_turning_noise)
        menu.add.range_slider('Sense noise:', default=self.sense_noise, range_values=(0, 20),increment=1, onchange=self.set_sense_noise)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def set_sense_noise(self, value):
        self.sense_noise = value

    def set_forward_noise(self, value):
        self.forward_noise = value

    def set_turning_noise(self, value):
        self.turning_noise = value

    def set_number_of_particles(self, value):
        self.number_of_particles = value

    def start_the_game(self):
        self.gui = particle_filter.ParticleFilterGUI(n_particles=self.number_of_particles,
                                                     forward_noise=self.forward_noise,
                                                     turning_noise=self.turning_noise,
                                                     sense_noise=self.sense_noise)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class KalmanFilter2DMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, surface, width, height, theme=theme)
        self.initial_uncertainty = 'big'
        self.step_size = 1
        self.motion_noise = 1
        self.sense_noise = 5

    def start_the_game(self):
        self.gui = kalman_filter_2d.Kalman_2D(motion_sigma=self.motion_noise, measurement_sigma=self.sense_noise,
                                              stepsize=self.step_size, initial_uncertainty=self.initial_uncertainty)
        self.gui.start()
        pygame.display.set_mode((600, 400))

    def controls(self):
        menu = pygame_menu.Menu('Kalman Filter 2D Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()
        table.add_row(['Up arrow', 'Move up'], cell_padding=8, cell_font_size=20)
        table.add_row(['Right arrow', 'Move right'], cell_padding=8, cell_font_size=20)
        table.add_row(['Down arrow', 'Move down'], cell_padding=8, cell_font_size=20)
        table.add_row(['Left arrow', 'Move left'], cell_padding=8, cell_font_size=20)
        table.add_row(['S', 'Sense environment'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def settings(self):
        menu = pygame_menu.Menu('Kalman Filter 2D Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.vertical_margin(25)
        menu.add.selector('Initial uncertainty:', [('small', 0), ('medium', 1), ('big', 2)],  default=2, onchange=self.set_init_uncertainty)
        menu.add.range_slider('Sense noise:', default=self.sense_noise, range_values=(0, 50), increment=1, onchange=self.set_sense_noise)
        menu.add.range_slider('Motion noise:', default=self.motion_noise, range_values=(0, 10), increment=1, onchange=self.set_motion_noise)
        menu.add.range_slider('Step size:', default=self.step_size, range_values=(1, 10), increment=1, onchange=self.set_step_size)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def set_init_uncertainty(self, value, num):
        self.initial_uncertainty = value[0][0]

    def set_step_size(self, value):
        self.step_size = value

    def set_motion_noise(self, value):
        self.motion_noise = value

    def set_sense_noise(self, value):
        self.sense_noise = value


class KalmanFilter1DMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, surface, width, height, theme=theme)
        self.initial_uncertainty = 'big'
        self.step_size = 1
        self.motion_noise = 1
        self.sense_noise = 5

    def start_the_game(self):
        self.gui = kalman_filter_1d.Kalman_1D(motion_sigma=self.motion_noise, measurement_sigma=self.sense_noise,
                                              stepsize=self.step_size, initial_uncertainty=self.initial_uncertainty)
        self.gui.start()
        pygame.display.set_mode((600, 400))

    def controls(self):
        menu = pygame_menu.Menu('Kalman Filter 1D Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()
        table.add_row(['Right arrow', 'Move right'], cell_padding=8, cell_font_size=20)
        table.add_row(['Left arrow', 'Move left'], cell_padding=8, cell_font_size=20)
        table.add_row(['S', 'Sense environment'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def settings(self):
        menu = pygame_menu.Menu('Kalman Filter 1D Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.vertical_margin(25)
        menu.add.selector('Initial uncertainty:', [('small', 0), ('medium', 1), ('big', 2)],  default=2, onchange=self.set_init_uncertainty)
        menu.add.range_slider('Sense noise:', default=self.sense_noise, range_values=(0, 50), increment=1, onchange=self.set_sense_noise)
        menu.add.range_slider('Motion noise:', default=self.motion_noise, range_values=(0, 10), increment=1, onchange=self.set_motion_noise)
        menu.add.range_slider('Step size:', default=self.step_size, range_values=(1, 10), increment=1, onchange=self.set_step_size)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def set_init_uncertainty(self, value, num):
        self.initial_uncertainty = value[0][0]

    def set_step_size(self, value):
        self.step_size = value

    def set_motion_noise(self, value):
        self.motion_noise = value

    def set_sense_noise(self, value):
        self.sense_noise = value


class MainGUI():
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((600, 400))
        pygame.display.set_caption('')
        self.game = None
        self.menu = pygame_menu.Menu('RoboLab', 600, 400,
                                theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.EXIT)
        self.image = None
        self.menu.add.text_input('Name :', default='UserName')
        self.menu.add.selector('Game :', [('Particle Filter', 1), ('Kalman Filter 1D', 2), ('Kalman Filter 2D', 2), ('A*', 3)], default=0, onchange=self.set_game)
        self.image = self.menu.add.image(os.path.join(env.images_path, 'spaceship.png'), scale=(0.25,0.25))
        self.menu.add.button('Next', self.start_the_game)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)
        self.game = 'Particle Filter'

    def start(self):
        self.menu.mainloop(self.surface)

    def set_game(self, value, game_num):
        self.game = value[0][0]
        match self.game:
            case 'Particle Filter':
                img_name = 'spaceship.png'
            case 'A*':
                img_name = 'flag.png'
            case 'Kalman Filter 2D' | 'Kalman Filter 1D':
                img_name = 'robot2.png'
        image = pygame_menu.baseimage.BaseImage(os.path.join(env.images_path, img_name))
        image = image.scale(0.25, 0.25)
        if self.image:
            self.image.set_image(image)

    def start_the_game(self, ):
        # Do the job here !
        match self.game:
            case 'A*':
                self.menu = AStarMenu('A*', self.surface)
            case 'Particle Filter':
                self.menu = ParticleMenu('Particle Filter', self.surface)
            case 'Kalman Filter 2D':
                self.menu = KalmanFilter2DMenu('Kalman Filter 2D', self.surface)
            case 'Kalman Filter 1D':
                self.menu = KalmanFilter1DMenu('Kalman Filter 1D', self.surface)
        self.menu.start()
        self.surface = pygame.display.set_mode((600, 400))


main_gui = MainGUI()
main_gui.start()