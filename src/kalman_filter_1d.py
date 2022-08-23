import sys
import random

from src import datatypes
import matplotlib.pyplot as plt
import numpy as np
import pygame as pg
import os
import env
from src import utils


class Kalman_1D(datatypes.RobotGUI):
    def __init__(self, screen_width=1000, stepsize=10, motion_sigma=10, measurement_sigma=10., initial_uncertainty='small'):
        super().__init__(screen_width=screen_width, height_width_ratio=2/3)
        self.step_size = stepsize
        self.moving = False
        self.motion = None
        robot_x = random.randint(0, self.screen_width-1)
        # start with big uncertainty
        match initial_uncertainty:
            case 'small':
                uncertainty_scale  = 1/2
            case 'medium':
                uncertainty_scale = 1e0
            case 'big':
                uncertainty_scale = 2
            case _:
                uncertainty_scale = 1

        self.cell_width = self.robot_size*1.2
        # self.world_size = self.screen_width
        self.plot_width = self.screen_width
        self.plot_height = self.screen_width/3
        self.screen_height = self.plot_height+self.cell_width

        sigma = self.world_size[0] * uncertainty_scale
        self.robot = datatypes.RobotKalman1D(true_position=robot_x, position_uncertainty=sigma, motion_uncertainty=motion_sigma,
                                   measurement_uncertainty=measurement_sigma, size=self.robot_size)

        # Parameters for plottig the gaussian. This only needs to be calculated once.
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, self.screen_width)
        ax.set_ylim(0, 0.1)
        self.fig = fig
        self.ax = ax
        self.x = np.linspace(0, self.screen_width, self.screen_width)
        self.plot_color='blue'

    def init_pygame(self):
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        self.robot_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, 'robot2.png')), (self.robot_size, self.robot_size))

    def handle_events(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    motion = -1 * self.step_size
                elif event.key == pg.K_RIGHT:
                    motion = 1 * self.step_size
                elif event.key == pg.K_ESCAPE:
                    return 1
                else:
                    motion = False
                if motion:
                    self.moving = True
                    self.motion = motion
                    self.plot_color = 'red'
                if event.key == pg.K_s:
                    self.robot.sense()
                    self.plot_color = 'blue'

            elif event.type == pg.KEYUP:
                self.moving = False
            elif event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        if self.moving:
            self.robot.move(self.motion)
        return 0

    def draw(self):
        rect = pg.Rect(0, self.plot_height, self.plot_width, self.cell_width)
        pg.draw.rect(self.screen, (200, 200, 200), rect, 0)
        gauss = self.plot2surface(self.robot.pos, self.robot.sigma)
        gauss = pg.transform.smoothscale(gauss, (self.plot_width, self.plot_height))
        self.screen.blit(gauss, (0, 0))
        self.screen.blit(self.robot_img, [self.robot.pos - self.robot_size / 2, self.plot_height + self.cell_width / 8])
        plt.close()

    def plot2surface(self, mu, sigma):
        self.fig.canvas.flush_events()
        gauss = self.ax.plot(self.x, utils.Gaussian(mu, sigma, self.x), color=self.plot_color)
        surface = utils.fig2surface(self.fig)
        for col in gauss:
            col.remove()
        return surface


if __name__ == "__main__":
    gui = Kalman_1D()
    gui.start()