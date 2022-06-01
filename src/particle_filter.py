import math
import os.path
import random
import sys

import matplotlib.pyplot as plt
import matplotlib

import env

matplotlib.use('Qt5Agg')


import pygame as pg

from src import utils
from src.datatypes import RobotGUI, RobotParticle

ANGULAR_STEP = 0.1
LINEAR_STEP = 0.3

#TODO
# check why ship seems to move slightly faster than arrows
# add more landmarks
# make moon orbit around the earth?
# implement blitting or use pyqtgraph to bring fps to >30


class ParticleFilterGUI(RobotGUI):
    def __init__(self, n_particles, forward_noise, turning_noise, sense_noise, n_planets):
        super().__init__(screen_width=1000, height_width_ratio=1/2, robot_img="spaceship")
        self.n_particles = n_particles
        self.n_planets = n_planets
        self.particles = [RobotParticle(world_size=self.world_size, forward_noise=forward_noise, turning_noise=turning_noise, sense_noise=sense_noise)
                          for _ in range(self.n_particles)]
        self.moving = False

        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor('xkcd:navy blue')

        ax.set_ylim([-5, self.world_size[1] + 5])
        ax.set_xlim([-5, self.world_size[0] + 5])
        self.fig = fig
        self.ax = ax
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
        self.landmarks_pos = [l['pos'] for l in list(self.landmarks.values())[:self.n_planets]]
        self.landmarks_imgs = []

    def init_pygame(self):
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height), pg.DOUBLEBUF)
        self.screen.fill('black')
        robot_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, f'{self.robot_img}.png')).convert_alpha(), (self.robot_size, self.robot_size))
        robot_img = pg.transform.rotozoom(robot_img, -90, 1)
        self.robot = RobotParticle(world_size=self.world_size, image=robot_img) if self.robot_type == 'diff' else None
        for landmark in list(self.landmarks.values())[:self.n_planets]:
            file = landmark['file']
            size = landmark['size']
            self.landmarks_imgs.append(pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, file)).convert_alpha(), (size, size)))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 1
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
                elif event.key == pg.K_ESCAPE:
                    return 1
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
            self.particles = utils.resample(particles=self.particles, weights=w, N=self.n_particles, robotclass=RobotParticle)
        return 0

    def plot2surface(self):
        X, Y, U, V = (list() for i in range(4))
        for p in self.particles:
            angle = p.orientation
            X.append(p.x)
            Y.append(p.y)
            U.append(math.cos(angle))
            V.append(math.sin(angle))

        self.fig.canvas.flush_events()
        Q = self.ax.quiver(X, Y, U, V, color='red', pivot='middle')

        surface = utils.fig2surface(self.fig)
        plt.close(self.fig)
        Q.remove()
        return surface

    def draw(self):
        plot = self.plot2surface()
        plot = pg.transform.smoothscale(plot, (self.screen_width, self.screen_height))
        self.screen.blit(plot, (0, 0))
        robotx, roboty = self.robot.get_position()
        robotx_screen, roboty_screen = self.world2screen((robotx, roboty))
        # center of the robot should coincide with center of the image instead of the upper left corner
        frame = self.robot.image.get_rect()
        frame.center = robotx_screen, roboty_screen
        self.screen.blit(self.robot.image, frame)
        for i, img in enumerate(self.landmarks_imgs):
            pos = self.world2screen(self.landmarks[i]['pos'])
            self.screen.blit(img, pos)


if __name__ == "__main__":
    particleGUI = ParticleFilterGUI(10, 0.05, 0.05, 5, 2)
    particleGUI.start(verbose=True, fps=30)
