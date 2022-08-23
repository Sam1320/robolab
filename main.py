import os

import pygame
import pygame_menu
import env
import src.menus as menus


class MainGUI():
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((env.MENU_WIDTH, env.MENU_HEIGHT))
        pygame.display.set_caption('')
        self.game = None
        self.menu = pygame_menu.Menu('RoboLab', env.MENU_WIDTH, env.MENU_HEIGHT,
                                theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.EXIT)
        self.image = None
        self.guis = [('Histogram Filter',),('Particle Filter',), ('Kalman Filter 1D',), ('Kalman Filter 2D',), ('A*',),
                     ('Dynamic Programming',), ('Optimum Policy',), ('Path Smoothing',), ('PID Control',)]
        self.menu.add.text_input('Name :', default='UserName')
        self.menu.add.selector('Game :', self.guis, default=0, onchange=self.set_game)
        self.image = self.menu.add.image(os.path.join(env.images_path, 'histogram_filter_thumbnail_resized.png'))
        self.menu.add.button('Next', self.start_the_game)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)
        self.game = self.guis[0][0]

    def start(self):
        self.menu.mainloop(self.surface)

    def set_game(self, value):
        self.game = value[0][0]
        match self.game:
            case 'Particle Filter':
                img_name = 'particle_filter_thumbnail_resized.png'
            case 'Kalman Filter 1D':
                img_name = 'kalman_1d_thumbnail_resized.png'
            case 'Kalman Filter 2D':
                img_name = 'kalman_2d_thumbnail_resized.png'
            case 'A*':
                img_name = 'a_star_thumbnail_resized.png'
            case 'Dynamic Programming':
                img_name = 'dynamic_programming_thumbnail_resized.png'
            case 'Optimum Policy':
                img_name = 'optimum_policy_thumbnail_resized.png'
            case 'Path Smoothing':
                img_name = 'path_smoothing_thumbnail_resized.png'
            case 'PID Control':
                img_name = 'pid_control_thumbnail_resized.png'
            case 'Histogram Filter':
                img_name = 'histogram_filter_thumbnail_resized.png'


        image = pygame_menu.baseimage.BaseImage(os.path.join(env.images_path, img_name))
        # image = image.scale(0.25, 0.25)/home/sam/Code/reinforcement-learning/openai-gym
        if self.image:
            self.image.set_image(image)

    def start_the_game(self, ):
        match self.game:
            case 'A*':
                self.menu = menus.AStarMenu('A*', self.surface)
            case 'Particle Filter':
                self.menu = menus.ParticleMenu('Particle Filter', self.surface)
            case 'Kalman Filter 2D':
                self.menu = menus.KalmanFilter2DMenu('Kalman Filter 2D', self.surface)
            case 'Kalman Filter 1D':
                self.menu = menus.KalmanFilter1DMenu('Kalman Filter 1D', self.surface)
            case 'Dynamic Programming':
                self.menu = menus.DynamicProgrammingMenu('Dynamic Programming', self.surface)
            case 'Optimum Policy':
                self.menu = menus.OptimumPolicyMenu('Optimum Policy', self.surface)
            case 'Path Smoothing':
                self.menu = menus.PathSmoothingMenu('Path Smoothing', self.surface)
            case 'PID Control':
                self.menu = menus.PIDControlMenu('PID Control', self.surface)
            case 'Histogram Filter':
                self.menu = menus.HistogramFilterMenu('Histogram Filter', self.surface)

        self.menu.start()
        self.surface = pygame.display.set_mode((env.MENU_WIDTH, env.MENU_HEIGHT))

main_gui = MainGUI()
main_gui.start()