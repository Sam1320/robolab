import math
import random
import sys

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


import pygame as pg

import utils
from datatypes import RobotGUI, RobotDiff

ANGULAR_STEP = 0.1
LINEAR_STEP = 0.2

#TODO
# check why ship seems to move slightly faster than arrows
# add more landmarks
# make moon orbit around the earth?
# improve fps to >11

class ParticleFilterGUI(RobotGUI):
    def __init__(self):
        super().__init__(height_width_ratio=1/2)
        self.n_particles = 800
        self.particles = [RobotDiff(world_size=self.world_size, forward_noise=0.05, turning_noise=0.05, sense_noise=5)
                          for _ in range(self.n_particles)]
        self.moving = False

        # plt.figure(figsize=self.figsize)
        # fig = plt.gcf()
        # ax = fig.add_axes([0, 0, 1, 1])
        # # ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
        #
        # ax.set_ylim([-5, self.world_size[1] + 5])
        # ax.set_xlim([-5, self.world_size[0] + 5])
        # self.fig = fig
        # self.ax = ax
        self.landmarks = {
            0:
                {'pos': (10, 30),
                 'file': 'planet-earth.png',
                 'size': self.robot_size * 2},
            1:
                {'pos': (15, 35),
                 'file': 'moon.png',
                 'size': self.robot_size},
            2:
                {'pos': (70, 30),
                 'file': 'mars.png',
                 'size': self.robot_size * 1.5}
        }
        self.landmarks_pos = [l['pos'] for l in self.landmarks.values()]
        self.landmarks_imgs = []
        for landmark in self.landmarks.values():
            file = landmark['file']
            size = landmark['size']
            self.landmarks_imgs.append(pg.transform.smoothscale(pg.image.load(file).convert_alpha(), (size, size)))

        pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])

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
            Z = self.robot.sense(self.landmarks_pos)
            w = []
            for p in self.particles:
                w.append(p.measurement_prob(Z, self.landmarks_pos))
            self.particles = utils.resample(particles=self.particles, weights=w, N=self.n_particles)

    def plot2surface(self):
        plt.figure(figsize=self.figsize)
        fig = plt.gcf()
        ax = fig.add_axes([0, 0, 1, 1])
        # ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])

        ax.set_ylim([-5, self.world_size[1] + 5])
        ax.set_xlim([-5, self.world_size[0] + 5])

        X, Y, U, V = (list() for i in range(4))
        for p in self.particles:
            angle = p.orientation
            X.append(p.x)
            Y.append(p.y)
            U.append(math.cos(angle))
            V.append(math.sin(angle))
        # self.ax.grid()
        ax.quiver(X, Y, U, V, color='red', pivot='middle')#, scale=1/4, units='xy', headwidth=3/2)

        surface = utils.fig2surface(fig)
        plt.close(fig)
        # self.ax.clear()
        return surface

    def draw(self):
        # plot = pg.transform.smoothscale(self.plot2surface(), (self.plot_width, self.plot_height))
        plot = self.plot2surface()
        self.screen.blit(plot, (self.panel_width, 0))
        robotx, roboty = self.robot.get_position()
        robotx_screen, roboty_screen = self.world2screen((robotx, roboty))
        # center of the robot should coincide with center of the image instead of the upper left corner
        frame = self.robot.image.get_rect()
        frame.center = robotx_screen, roboty_screen
        self.screen.blit(self.robot.image, frame)
        for i, img in enumerate(self.landmarks_imgs):
            pos = self.world2screen(self.landmarks[i]['pos'])
            self.screen.blit(img, pos)


particleGUI = ParticleFilterGUI()
particleGUI.start()

# plt.grid()
# plt.quiver([10, 11], [40, 11], [0, 1], [1, 0])
# plt.show()
