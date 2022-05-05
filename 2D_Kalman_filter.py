import sys
import random

import numpy as np
import pygame as pg
from matplotlib import pyplot as plt
from scipy.stats import multivariate_normal

import utils
from datatypes import RobotGUI

dpi =  utils.get_dpi()

#TODO
# use RobotGUI

class RobotKalman2D():
    def __init__(self, true_position, position_uncertainty, motion_uncertainty, measurement_uncertainty, size):
        self.pos = true_position
        self.mu = list(true_position)
        self.sigma = position_uncertainty
        self.measurement_sigma = measurement_uncertainty
        self.motion_sigma = motion_uncertainty
        self.size = size
        # self.world_size = world_size

    def move(self, motion):
        # motion update. Predict new position and variance.
        if motion[0]:
            self.mu[0] += motion[0]
            self.sigma[0][0] = np.sqrt(self.sigma[0][0]**2 + self.motion_sigma**2)
            #todo: noise for actual movement should be lower(?)
            self.pos[0] += np.random.normal(motion[0], self.motion_sigma, 1)[0]
        elif motion[1]:
            self.mu[1] += motion[1]
            self.sigma[1][1] = np.sqrt(self.sigma[1][1]**2 + self.motion_sigma**2)
            self.pos[1] += np.random.normal(motion[1], self.motion_sigma, 1)[0]

    def sense(self):
        measurement = np.random.multivariate_normal(self.pos, self.measurement_sigma, 1)[0]
        self.mu[0] = (self.mu[0]*(self.measurement_sigma[0][0]**2) + measurement[0]*self.sigma[0][0]**2)/ (self.sigma[0][0]**2+self.measurement_sigma[0][0]**2)
        self.mu[1] = (self.mu[1]*(self.measurement_sigma[1][1]**2) + measurement[1]*self.sigma[1][1]**2)/ (self.sigma[1][1]**2+self.measurement_sigma[1][1]**2)
        self.sigma[0][0] = np.sqrt(1/(1/self.sigma[0][0]**2 + 1/self.measurement_sigma[0][0]**2))
        self.sigma[1][1] = np.sqrt(1/(1/self.sigma[1][1]**2 + 1/self.measurement_sigma[0][0]**2))


class Kalman_2D:
    def __init__(self, screen_width=1500, font_size=0):
        self.screen_width = screen_width
        self.height_width_ratio = 2/3
        self.screen_height = int(screen_width*self.height_width_ratio)
        input_width = font_size * 2
        input_height = font_size * 1.5
        label_width = font_size * 8
        label_height = font_size * 1.5
        self.dpi = dpi
        self.world_size = (100, int(100*self.height_width_ratio))
        self.robot_size = self.screen_width//30
        self.step_size = 5
        self.panel_width = input_width + label_width
        self.cell_width = self.robot_size*1.2
        self.robot_img = pg.transform.smoothscale(pg.image.load('robot2.png'), (self.robot_size, self.robot_size))

        self.plot_width = self.screen_width - self.panel_width
        self.plot_height = self.screen_height
        self.figsize = (int(self.plot_width/self.dpi), int(self.plot_height/self.dpi))
        self.font_size = font_size
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        robot_x = 50 #random.randint(10, self.world_size[0]-10)
        robot_y = 50 #random.randint(10, self.world_size[0]-10)
        mu = [robot_x, robot_y]
        # start with big uncertainty
        sigma = [[self.world_size[0]*10, 0], [0, self.world_size[1]*10]]

        motion_sigma = 1.
        measurement_sigma = [[2., 0], [0., 2.]]
        self.robot = RobotKalman2D(mu, sigma, motion_uncertainty=motion_sigma, measurement_uncertainty=measurement_sigma, size=self.robot_size)
        self.outline = 2

        # Parameters for plottig the gaussian. This only needs to be calculated once.
        self.x_mesh, self.y_mesh = np.mgrid[0:self.world_size[0]:0.5, self.world_size[1]:0:-0.5]
        self.mesh_coords = np.dstack((self.x_mesh, self.y_mesh))
        self.x_ticks = np.arange(0, self.world_size[0], self.world_size[0]/20)
        self.y_ticks = np.arange(1, self.world_size[1], self.world_size[1]/20)

    def start(self):
        pg.init()
        self.screen.fill('black')
        while True:
            self.drawgrid()
            self.handle_events()
            pg.display.flip()

    def handle_events(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    motion = (-1 * self.step_size, 0)
                elif event.key == pg.K_RIGHT:
                    motion = (1 * self.step_size, 0)
                elif event.key == pg.K_DOWN:
                    motion = (0, 1 * self.step_size)
                elif event.key == pg.K_UP:
                    motion = (0, -1 * self.step_size)
                else:
                    motion = False
                if motion:
                    # bound motion to the limits of the world
                    if 0 < motion[0] + self.robot.pos[0] < self.world_size[0] and 0 < motion[1] + self.robot.pos[1] < \
                            self.world_size[1]:
                        self.robot.move(motion)
                if event.key == pg.K_m:
                    self.robot.sense()

    def drawgrid(self):

        gauss = self.gauss2surface(self.robot.mu, self.robot.sigma)
        gauss = pg.transform.smoothscale(gauss, (self.plot_width, self.plot_height))
        self.screen.blit(gauss, (self.panel_width, 0))
        robotx, roboty = self.world2screen(self.robot.pos)
        self.screen.blit(self.robot_img, [(robotx)-self.robot.size//2, roboty-(self.robot.size//2)])

        plt.close()

    def world2screen(self, pos):
        x, y = pos[0], pos[1]
        x_norm = x/self.world_size[0]
        y_norm = y/self.world_size[1]
        new_y = self.screen_height*y_norm
        new_x = self.screen_width*x_norm
        new_x += self.panel_width
        return new_x, new_y

    def gauss2surface(self, mu, sigma):
        rv = multivariate_normal(mu, sigma)
        z = rv.pdf(self.mesh_coords)
        plt.figure(figsize=self.figsize)
        fig = plt.gcf()
        # ax = fig.gca()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.invert_yaxis()
        # ax.set_axis_off()
        # levels = [0.0000005, 0.000001, 0.00001, 0.0001, 0.0002, 0.00025]
        cs = ax.contourf(self.x_mesh, self.y_mesh, z, levels=5, cmap='coolwarm')
        # ax.contour(cs, colors='k')

        ax.set_xticks(self.x_ticks)
        ax.set_yticks(self.y_ticks)

        # And a corresponding grid
        ax.grid(c='k', ls='-', alpha=0.3)
        return utils.fig2surface(fig)

kf = Kalman_2D()
kf.start()