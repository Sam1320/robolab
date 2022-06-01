import os

import pygame
import pygame_menu


import env
from src import datatypes, a_star, particle_filter, kalman_filter_1d, kalman_filter_2d, dynamic_programming, \
    optimum_policy, path_smoothing, pid_control, histogram_filter


class GameMenu(pygame_menu.Menu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, width, height, theme=theme, onclose=pygame_menu.events.BACK)
        self.add.button('Controls', self.controls)
        self.add.button('Settings', self.settings)
        self.add.button('Play', self.start_the_game)
        self.add.button('Back', self.go_back)
        self.surface = surface
        self.gui_class = datatypes.RobotGUI
        self.name = name

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


class GridMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400, max_grid_width=50, max_grid_height=50):
        super().__init__(name, surface, width, height)
        self.width = 10
        self.height = 10
        self.surface = surface
        self.load_map = 0
        self.obstacle_prob = 0.2
        self.max_grid_width = max_grid_width
        self.max_grid_height = max_grid_height

    def controls(self):
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()
        table.add_row(['Right click', 'set goal position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Middle click', 'modify map'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        table.add_row(['Enter', 'save map'], cell_padding=8, cell_font_size=20)

        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def settings(self):
        menu = pygame_menu.Menu(f'{self.name} Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.toggle_switch('Load Map:', default=self.load_map, onchange=self.set_map_load)
        menu.add.range_slider('Obstacle Probability:', default=self.obstacle_prob, range_values=[0, 0.2, 0.4, 0.6, 0.8, 1], onchange=self.set_obstacle_prob)
        menu.add.range_slider('Grid Width :', default=self.width, range_values=(1, self.max_grid_width), increment=1, onchange=self.set_width)
        menu.add.range_slider('Grid Height :', default=self.height, range_values=(1, self.max_grid_height), increment=1, onchange=self.set_height)
        menu.add.button('Save', menu.close)
        menu.mainloop(self.surface)

    def set_obstacle_prob(self, value):
        self.obstacle_prob = value

    def set_map_load(self, value):
        self.load_map = value

    def set_width(self, value):
        self.width = int(value)

    def set_height(self, value):
        self.height = int(value)


class AStarMenu(GridMenu):
    def __init__(self, name, surface, width=600, height=400):
        super().__init__(name, surface, width, height)
        self.path_arrows = False

    def controls(self):
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()
        table.add_row(['Left click', 'set start position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Right click', 'set goal position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Middle click', 'modify map'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        table.add_row(['Enter', 'save map'], cell_padding=8, cell_font_size=20)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def settings(self):
        menu = pygame_menu.Menu(f'{self.name} Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.toggle_switch('Load Map:', default=self.load_map, onchange=self.set_map_load)
        menu.add.selector('Path Type:', [('Color',), ('Arrows',)], default=self.path_arrows, onchange=self.set_path_type)
        menu.add.range_slider('Obstacle Probability:', default=self.obstacle_prob, range_values=[0, 0.2, 0.4, 0.6, 0.8, 1], onchange=self.set_obstacle_prob)
        menu.add.range_slider('Grid Width :', default=self.width, range_values=(1, 50), increment=1, onchange=self.set_width)
        menu.add.range_slider('Grid Height :', default=self.height, range_values=(1, 50), increment=1, onchange=self.set_height)
        menu.add.button('Save', menu.close)
        menu.mainloop(self.surface)

    def set_path_type(self, value):
        if value[0][0] == 'Arrows':
            self.path_arrows = True
        else:
            self.path_arrows = False

    def start_the_game(self):
        self.gui = a_star.AStartGUI(world_size=(self.width, self.height), load_grid=self.load_map,
                                    obstacle_prob=self.obstacle_prob, path_arrows=self.path_arrows)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class PathSmoothingMenu(GridMenu):
    def __init__(self, name, surface, width=600, height=400, max_grid_width=20, max_grid_height=20):
        super().__init__(name, surface, width, height, max_grid_width=max_grid_width, max_grid_height=max_grid_height)

    def controls(self):
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()

        table.add_row(['Left click', 'set start position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Right click', 'set goal position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Middle click', 'modify map'], cell_padding=8, cell_font_size=20)
        table.add_row(['Mouse wheel', 'adjust path smoothness'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        table.add_row(['Enter', 'save map'], cell_padding=8, cell_font_size=20)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def start_the_game(self):
        self.gui = path_smoothing.PathSmoothingGUI(world_size=(self.width, self.height))
        self.gui.start()
        pygame.display.set_mode((600, 400))


class PIDControlMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400,
                 x_init=0, y_init=0.1, drift=0,
                 proportional_gain=0.1,
                 integral_gain=0,
                 differential_gain=0):
        super().__init__(name, surface, width, height)
        self.x_init = x_init
        self.y_init = y_init
        self.drift = drift
        self.proportional_gain = proportional_gain
        self.integral_gain = integral_gain
        self.differential_gain = differential_gain

    def settings(self):
        menu = pygame_menu.Menu(f'{self.name} Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.vertical_margin(25)
        menu.add.range_slider('X Initial:', default=self.x_init, range_values=(-1, 1), increment=0.05, onchange=self.set_x_init)
        menu.add.range_slider('Y Initial:', default=self.y_init, range_values=(-1, 1), increment=0.05, onchange=self.set_y_init)
        menu.add.range_slider('Drift:', default=self.drift, range_values=(-30, 30), increment=5, onchange=self.set_drift)
        menu.add.range_slider('Proportional Gain:', default=self.proportional_gain, range_values=(0, 1), increment=0.01, onchange=self.set_proportional_gain)
        menu.add.range_slider('Integral Gain:', default=self.integral_gain, range_values=(0, 0.5), increment=0.005, onchange=self.set_integral_gain)
        menu.add.range_slider('Differential Gain:', default=self.differential_gain, range_values=(0, 5), increment=0.5, onchange=self.set_differential_gain)
        menu.add.button('Save', menu.close)
        menu.mainloop(self.surface)

    def controls(self):
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()
        table.add_row(['Left click', 'increase speed'], cell_padding=8, cell_font_size=20)
        table.add_row(['Right click', 'decrease speed'], cell_padding=8, cell_font_size=20)
        table.add_row(['Up arrow', 'increase drift'], cell_padding=8, cell_font_size=20)
        table.add_row(['Down arrow', 'decrease drift'], cell_padding=8, cell_font_size=20)
        table.add_row(['T', 'Find best parameters with Twiddle'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        table.add_row(['Enter', 'save map'], cell_padding=8, cell_font_size=20)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def set_x_init(self, value):
        self.x_init = value

    def set_y_init(self, value):
        self.y_init = value

    def set_drift(self, value):
        self.drift = value

    def set_proportional_gain(self, value):
        self.proportional_gain = value

    def set_integral_gain(self, value):
        self.integral_gain = value

    def set_differential_gain(self, value):
        self.differential_gain = value

    def start_the_game(self):
        self.gui = pid_control.PIDControlGUI(x_init=self.x_init, y_init=self.y_init, drift=self.drift,
                                     proportional_gain=self.proportional_gain, integral_gain=self.integral_gain,
                                     differential_gain=self.differential_gain)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class OptimumPolicyMenu(GridMenu):
    def __init__(self, name, surface, width=600, height=400):
        super().__init__(name, surface, width, height)
        self.move_right_cost = 1
        self.move_left_cost = 1
        self.move_forward_cost = 1
        self.init_orientation = 0
        self.path_arrows = True

    def controls(self):
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()
        table.add_row(['Left click', 'set start position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Right click', 'set goal position'], cell_padding=8, cell_font_size=20)
        table.add_row(['Middle click', 'modify map'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        table.add_row(['Enter', 'save map'], cell_padding=8, cell_font_size=20)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def settings(self):
        menu = pygame_menu.Menu(f'{self.name} Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.toggle_switch('Load Map', default=self.load_map, onchange=self.set_map_load)
        menu.add.selector('Path Type:', [('Color',), ('Arrows',)], default=self.path_arrows, onchange=self.set_path_type)
        menu.add.selector('Initial Orientation', [('UP', 0), ('LEFT', 1), ('DOWN', 2), ('RIGHT', 3)],
                          default=self.init_orientation, onchange=self.set_init_orientation)
        menu.add.range_slider('Move Left Cost', default=self.move_left_cost,
                              range_values=(1, 20), increment=1, onchange=self.set_move_left_cost)
        menu.add.range_slider('Move Forward Cost', default=self.move_forward_cost,
                              range_values=(1, 20), increment=1, onchange=self.set_move_forward_cost)
        menu.add.range_slider('Move Right Cost', default=self.move_right_cost,
                              range_values=(1, 20), increment=1, onchange=self.set_move_right_cost)
        menu.add.range_slider('Obstacle Probability:', default=self.obstacle_prob,
                              range_values=[0, 0.2, 0.4, 0.6, 0.8, 1], onchange=self.set_obstacle_prob)
        menu.add.range_slider('Grid Width :', default=self.width,
                              range_values=(1, 50), increment=1, onchange=self.set_width)
        menu.add.range_slider('Grid Height :', default=self.height,
                              range_values=(1, 50), increment=1, onchange=self.set_height)
        menu.add.button('Save', menu.close)
        menu.mainloop(self.surface)

    def set_path_type(self, value):
        if value[0][0] == 'Arrows':
            self.path_arrows = True
        else:
            self.path_arrows = False

    def set_init_orientation(self, value, num):
        self.init_orientation = num

    def set_move_right_cost(self, value):
        self.move_right_cost = value

    def set_move_left_cost(self, value):
        self.move_left_cost = value

    def set_move_forward_cost(self, value):
        self.move_forward_cost = value

    def start_the_game(self):
        costs = [self.move_right_cost, self.move_forward_cost, self.move_left_cost]
        self.gui = optimum_policy.OptimumPolicyGUI(world_size=(self.width, self.height), load_grid=self.load_map,
                                                   obstacle_prob=self.obstacle_prob, costs=costs,
                                                   init_orientation=self.init_orientation, path_arrows=self.path_arrows)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class DynamicProgrammingMenu(GridMenu):
    def __init__(self, name, surface, width=600, height=400):
        super().__init__(name, surface, width, height)

    def start_the_game(self):
        self.gui = dynamic_programming.DynamicProgrammingGUI(world_size=(self.width, self.height), load_grid=self.load_map,
                                                             obstacle_prob=self.obstacle_prob)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class ParticleMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, surface, width, height, theme=theme)

        self.number_of_particles = 200
        self.forward_noise = 0.05
        self.turning_noise = 0.05
        self.sense_noise = 5
        self.number_of_planets = 3
        self.gui = None

    def controls(self):
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
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
        menu = pygame_menu.Menu(f'{self.name} Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.vertical_margin(25)
        menu.add.range_slider('Number of Particles:', default=self.number_of_particles, range_values=[10, 100, 200, 400, 800], onchange=self.set_number_of_particles)
        menu.add.range_slider('Number of Celestial Bodies:', default=self.number_of_planets, range_values=(1, 7), increment=1, onchange=self.set_number_of_planets)
        menu.add.range_slider('Forward noise:', default=self.forward_noise, range_values=(0, 5), increment=0.05, onchange=self.set_forward_noise)
        menu.add.range_slider('Turning noise:', default=self.turning_noise, range_values=(0, 5), increment=0.05, onchange=self.set_turning_noise)
        menu.add.range_slider('Sense noise:', default=self.sense_noise, range_values=(0, 20), increment=1, onchange=self.set_sense_noise)
        menu.add.button('Save', menu.close)
        menu.mainloop(self.surface)

    def set_sense_noise(self, value):
        self.sense_noise = value

    def set_forward_noise(self, value):
        self.forward_noise = value

    def set_turning_noise(self, value):
        self.turning_noise = value

    def set_number_of_particles(self, value):
        self.number_of_particles = value

    def set_number_of_planets(self, value):
        self.number_of_planets = value

    def start_the_game(self):
        self.gui = particle_filter.ParticleFilterGUI(n_particles=self.number_of_particles,
                                                     forward_noise=self.forward_noise,
                                                     turning_noise=self.turning_noise,
                                                     sense_noise=self.sense_noise,
                                                     n_planets=self.number_of_planets)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class KalmanFilter2DMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, surface, width, height, theme=theme)
        self.initial_uncertainty = 'big'
        self.step_size = 1
        self.motion_noise = 1
        self.sense_noise = 5

    def controls(self):
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
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
        menu = pygame_menu.Menu(f'{self.name} Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.vertical_margin(25)
        menu.add.selector('Initial uncertainty:', [('small', 0), ('medium', 1), ('big', 2)],  default=2, onchange=self.set_init_uncertainty)
        menu.add.range_slider('Sense noise:', default=self.sense_noise, range_values=(0, 50), increment=1, onchange=self.set_sense_noise)
        menu.add.range_slider('Motion noise:', default=self.motion_noise, range_values=(0, 10), increment=1, onchange=self.set_motion_noise)
        menu.add.range_slider('Step size:', default=self.step_size, range_values=(1, 10), increment=1, onchange=self.set_step_size)
        menu.add.button('Save', menu.close)
        menu.mainloop(self.surface)

    def set_init_uncertainty(self, value, num):
        self.initial_uncertainty = value[0][0]

    def set_step_size(self, value):
        self.step_size = value

    def set_motion_noise(self, value):
        self.motion_noise = value

    def set_sense_noise(self, value):
        self.sense_noise = value

    def start_the_game(self):
        self.gui = kalman_filter_2d.Kalman_2D(motion_sigma=self.motion_noise, measurement_sigma=self.sense_noise,
                                              stepsize=self.step_size, initial_uncertainty=self.initial_uncertainty)
        self.gui.start()
        pygame.display.set_mode((600, 400))


class HistogramFilterMenu(GameMenu):
    def __init__(self, name, surface, width=600, height=400, theme=pygame_menu.themes.THEME_SOLARIZED):
        super().__init__(name, surface, width, height, theme=theme)
        # robot motion and sensing probabilities
        self.pHit = .9
        self.pMiss = 0.1
        self.pGood = .8
        self.pOvershoot = 0.5
        self.pUndershoot = 1 - self.pOvershoot
        self.grid_width = 10
        self.grid_height = 10

    def controls(self):
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED,
                                onclose=pygame_menu.events.BACK)
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
        menu = pygame_menu.Menu(f'{self.name} Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED,
                                onclose=pygame_menu.events.BACK)
        menu.add.vertical_margin(25)
        menu.add.range_slider('Grid Width :', default=self.grid_width, range_values=(1, 50), increment=1, onchange=self.set_width)
        menu.add.range_slider('Grid Height :', default=self.grid_height, range_values=(1, 50), increment=1, onchange=self.set_height)
        menu.add.range_slider('Good probability:', default=self.pGood, range_values=(0, 1), increment=0.1,
                                onchange=self.set_pGood)
        self.overshoot_slider = menu.add.range_slider('Overshoot Probability:', default=self.pOvershoot, range_values=(0, 1), increment=0.1,
                              onchange=self.set_overshoot_prob)
        self.undershoot_slider = menu.add.range_slider('Undershoot Probability:', default=self.pUndershoot, range_values=(0, 1), increment=0.1,
                                onchange=self.set_undershoot_prob)
        menu.add.range_slider('Hit Probability:', default=self.pHit, range_values=(0, 1), increment=0.1,
                                onchange=self.set_hit_prob)
        menu.add.range_slider('Miss Probability:', default=self.pMiss, range_values=(0, 1), increment=0.1,
                                onchange=self.set_miss_prob)
        menu.add.button('Save', menu.close)
        menu.mainloop(self.surface)

    def set_width(self, value):
        self.grid_width = value

    def set_height(self, value):
        self.grid_height = value

    def set_pGood(self, value):
        self.pGood = value

    def set_overshoot_prob(self, value):
        self.pOvershoot = value
        self.pUndershoot = (1 - self.pOvershoot)
        self.undershoot_slider.set_value(self.pUndershoot)

    def set_undershoot_prob(self, value):
        self.pUndershoot = value
        self.pOvershoot = (1 - self.pUndershoot)
        self.overshoot_slider.set_value(self.pOvershoot)

    def set_hit_prob(self, value):
        self.pHit = value

    def set_miss_prob(self, value):
        self.pMiss = value

    def start_the_game(self):
        self.gui = histogram_filter.HistogramFilterGUI(world_size=(self.grid_width, self.grid_height), pHit=self.pHit,
                                                       pMiss=self.pMiss, pGood=self.pGood, pOvershoot=self.pOvershoot,
                                                       pUndershoot=self.pUndershoot)
        self.gui.start()
        pygame.display.set_mode((600, 400))


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
        menu = pygame_menu.Menu(f'{self.name} Controls', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        table = menu.add.table()
        table.add_row(['Right arrow', 'Move right'], cell_padding=8, cell_font_size=20)
        table.add_row(['Left arrow', 'Move left'], cell_padding=8, cell_font_size=20)
        table.add_row(['S', 'Sense environment'], cell_padding=8, cell_font_size=20)
        table.add_row(['Escape', 'Exit game'], cell_padding=8, cell_font_size=20)
        menu.add.button('Back', menu.close)
        menu.mainloop(self.surface)

    def settings(self):
        menu = pygame_menu.Menu(f'{self.name} Settings', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.BACK)
        menu.add.vertical_margin(25)
        menu.add.selector('Initial uncertainty:', [('small', 0), ('medium', 1), ('big', 2)],  default=2, onchange=self.set_init_uncertainty)
        menu.add.range_slider('Sense noise:', default=self.sense_noise, range_values=(0, 50), increment=1, onchange=self.set_sense_noise)
        menu.add.range_slider('Motion noise:', default=self.motion_noise, range_values=(0, 10), increment=1, onchange=self.set_motion_noise)
        menu.add.range_slider('Step size:', default=self.step_size, range_values=(1, 10), increment=1, onchange=self.set_step_size)
        menu.add.button('Save', menu.close)
        menu.mainloop(self.surface)

    def set_init_uncertainty(self, value, num):
        self.initial_uncertainty = value[0][0]

    def set_step_size(self, value):
        self.step_size = value

    def set_motion_noise(self, value):
        self.motion_noise = value

    def set_sense_noise(self, value):
        self.sense_noise = value
