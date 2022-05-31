import os

import pygame
import pygame_menu
import env
import src.menus as menus


class MainGUI():
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((600, 400))
        pygame.display.set_caption('')
        self.game = None
        self.menu = pygame_menu.Menu('RoboLab', 600, 400,
                                theme=pygame_menu.themes.THEME_SOLARIZED, onclose=pygame_menu.events.EXIT)
        self.image = None
        self.guis = [('Particle Filter',), ('Kalman Filter 1D',), ('Kalman Filter 2D',), ('A*',),
                     ('Dynamic Programming',), ('Optimum Policy',), ('Path Smoothing',), ('PID Control',)]
        self.menu.add.text_input('Name :', default='UserName')
        self.menu.add.selector('Game :', self.guis, default=0, onchange=self.set_game)
        self.image = self.menu.add.image(os.path.join(env.images_path, 'spaceship.png'), scale=(0.25,0.25))
        self.menu.add.button('Next', self.start_the_game)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)
        self.game = 'Particle Filter'

    def start(self):
        self.menu.mainloop(self.surface)

    def set_game(self, value):
        self.game = value[0][0]
        match self.game:
            case 'Particle Filter':
                img_name = 'spaceship.png'
            case 'A*' | 'Dynamic Programming' | 'Path Smoothing':
                img_name = 'flag.png'
            case 'Kalman Filter 2D' | 'Kalman Filter 1D':
                img_name = 'robot2.png'
            case 'Optimum Policy' | 'PID Control':
                img_name = 'car.png'

        image = pygame_menu.baseimage.BaseImage(os.path.join(env.images_path, img_name))
        image = image.scale(0.25, 0.25)
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

        self.menu.start()
        self.surface = pygame.display.set_mode((600, 400))

main_gui = MainGUI()
main_gui.start()