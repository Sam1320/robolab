import math
import sys

import matplotlib.pyplot as plt
import pygame as pg

import utils
from datatypes import RobotGUI, RobotDiff

ANGULAR_STEP = 0.1
LINEAR_STEP = 0.2


class ParticleFilterGUI(RobotGUI):
    def __init__(self):
        super().__init__()
        self.particles = [RobotDiff(world_size=self.world_size) for _ in range(10)]
        self.moving = False

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                angular, linear = 0, 0
                if event.key == pg.K_LEFT:
                    angular = 1 * ANGULAR_STEP
                elif event.key == pg.K_RIGHT:
                    angular = -1 * ANGULAR_STEP
                elif event.key == pg.K_UP:
                    linear = 1 * LINEAR_STEP
                elif event.key == pg.K_DOWN:
                    linear = -1 * LINEAR_STEP
                self.linear = linear
                self.angular = angular
                self.moving = True
            elif event.type == pg.KEYUP:
                self.moving = False

        if self.moving:
            self.robot.move(self.linear, self.angular)
            for p in self.particles:
                p.move(self.linear, self.angular)

    def plot2surface(self):
        plt.figure(figsize=self.figsize)
        fig = plt.gcf()
        ax = fig.add_axes([0, 0, 1, 1])
        X, Y, U, V = (list() for i in range(4))
        for p in self.particles:
            angle = p.orientation
            X.append(p.x)
            Y.append(p.y)
            U.append(math.cos(angle))
            V.append(math.sin(angle))
        ax.quiver(X, Y, U, V)
        # plt.xlim(self.world_size[0])
        # plt.ylim(self.world_size[1])
        ax.grid()
        plt.close()
        return utils.fig2surface(fig)

    def draw(self):
        plot = self.plot2surface()
        self.screen.blit(plot, (self.panel_width, 0))
        robotx, roboty = self.robot.get_position()
        robotx_screen, roboty_screen = self.world2screen((robotx, roboty))
        # center of the robot should coincide with center of the image instead of the upper left corner
        frame = self.robot.image.get_rect()
        frame.center = robotx_screen, roboty_screen
        pg.draw.rect(self.screen, (0, 0, 0), frame, 1)
        self.screen.blit(self.robot.image, frame)

particleGUI = ParticleFilterGUI()
particleGUI.start()

# plt.grid()
# plt.quiver([10, 11], [40, 11], [0, 1], [1, 0])
# plt.show()