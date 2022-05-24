import os
import sys
import random

import numpy as np
import pygame as pg
from matplotlib import pyplot as plt
from scipy.stats import multivariate_normal

import env
from src import utils

from src import datatypes


class Kalman_2D(datatypes.RobotGUI):
    def __init__(self, screen_width=1000, stepsize=1, motion_sigma=1, measurement_sigma=10., initial_uncertainty='big'):
        super().__init__(screen_width=screen_width, height_width_ratio=2/3)
        self.step_size = stepsize
        self.cell_width = self.robot_size*1.2
        self.moving = False
        self.motion = None
        robot_x = 50
        robot_y = 50
        mu = [robot_x, robot_y]
        # start with big uncertainty
        match initial_uncertainty:
            case 'small':
                uncertainty_scale  = 1e0
            case 'medium':
                uncertainty_scale = 1e1
            case 'big':
                uncertainty_scale = 1e5
        sigma = [[self.world_size[0] * uncertainty_scale, 0], [0, self.world_size[1] * uncertainty_scale]]
        measurement_sigma = [[measurement_sigma, 0], [0., measurement_sigma]]
        self.robot = datatypes.RobotKalman2D(mu, sigma, motion_uncertainty=motion_sigma,
                                   measurement_uncertainty=measurement_sigma, size=self.robot_size)

        # Parameters for plottig the gaussian. This only needs to be calculated once.
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.grid_obstacles(c='k', ls='-', alpha=0.3)
        self.fig = fig
        self.ax = ax
        self.x_mesh, self.y_mesh = np.mgrid[0:self.world_size[0]:0.5, self.world_size[1]:0:-0.5]
        self.mesh_coords = np.dstack((self.x_mesh, self.y_mesh))
        self.x_ticks = np.arange(0, self.world_size[0], self.world_size[0]/20)
        self.y_ticks = np.arange(1, self.world_size[1], self.world_size[1]/20)

    def init_pygame(self):
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        self.robot_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, 'robot2.png')), (self.robot_size, self.robot_size))

    def handle_events(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    motion = (-1 * self.step_size, 0)
                elif event.key == pg.K_RIGHT:
                    motion = (1 * self.step_size, 0)
                elif event.key == pg.K_DOWN:
                    motion = (0, -1 * self.step_size)
                elif event.key == pg.K_UP:
                    motion = (0, 1 * self.step_size)
                elif event.key == pg.K_ESCAPE:
                    return 1
                else:
                    motion = None
                if motion:
                    self.motion = motion
                    self.moving = True
                if event.key == pg.K_s:
                    self.robot.sense()
            elif event.type == pg.KEYUP:
                self.moving = False
        if self.moving:
            self.robot.move(self.motion)
        return 0

    def draw(self):
        gauss = self.plot2surface(self.robot.mu, self.robot.sigma)
        gauss = pg.transform.smoothscale(gauss, (self.screen_width, self.screen_height))
        self.screen.blit(gauss, (0, 0))
        robotx, roboty = self.world2screen(self.robot.pos)
        self.screen.blit(self.robot_img, [(robotx)-self.robot.size//2, roboty-(self.robot.size//2)])


    def plot2surface(self, mu, sigma):
        rv = multivariate_normal(mu, sigma)
        z = rv.pdf(self.mesh_coords)
        self.fig.canvas.flush_events()
        cs = self.ax.contourf(self.x_mesh, self.y_mesh, z, levels=5, cmap='coolwarm')
        surface = utils.fig2surface(self.fig)
        plt.close()
        for coll in cs.collections:
            coll.remove()
        return surface

if __name__ == "__main__":
    kf = Kalman_2D()
    kf.start()