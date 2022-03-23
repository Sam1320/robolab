import sys
import random

import numpy as np
import pygame as pg
from matplotlib import pyplot as plt
from scipy.stats import multivariate_normal

import utils


def get_dpi():
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    screen = app.screens()[0]
    dpi = screen.physicalDotsPerInch()
    app.quit()
    return dpi
dpi =  get_dpi()

class Robot:
    def __init__(self, true_position, position_uncertainty, motion_uncertainty, size):
        self.pos = true_position
        self.mu = true_position
        self.sigma = position_uncertainty
        self.motion_sigma = motion_uncertainty
        self.size = size
        # self.world_size = world_size

    def move(self, motion):
        # motion update. Predict new position and variance.
        if motion[0]:
            self.mu[0] += motion[0]
            self.sigma[0][0] = np.sqrt(self.sigma[0][0]**2 + self.motion_sigma**2)
            self.pos[0] += np.random.normal(motion[0], self.motion_sigma, 1)[0]
        elif motion[1]:
            self.mu[1] += motion[1]
            self.sigma[1][1] = np.sqrt(self.sigma[1][1]**2 + self.motion_sigma**2)
            self.pos[1] += np.random.normal(motion[1], self.motion_sigma, 1)[0]


    def bound_position(self, position):
        #todo: bound movements to grid limits
        return position


class Kalman_2D:
    def __init__(self, screen_width=1500, font_size=0):
        self.screen_width = screen_width
        self.screen_height = screen_width//2
        input_width = font_size * 2
        input_height = font_size * 1.5
        label_width = font_size * 8
        label_height = font_size * 1.5
        self.dpi = dpi
        self.robot_size = self.screen_width//30
        self.step_size = 10
        self.panel_width = input_width + label_width
        self.cell_width = self.robot_size*1.2
        self.robot_img = pg.transform.smoothscale(pg.image.load('robot2.png'), (self.robot_size, self.robot_size))

        self.plot_width = self.screen_width - self.panel_width
        self.plot_height = self.screen_height
        self.figsize = (int(self.plot_width/self.dpi), int(self.plot_height/self.dpi))
        self.font_size = font_size
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        robot_x = random.randint(self.robot_size, self.screen_width-self.robot_size)
        robot_y = random.randint(self.robot_size, self.screen_height-self.robot_size)
        mu = [robot_x, robot_y]
        # start with big uncertainty
        # sigma = [[(self.screen_width+self.panel_width)*40, 2.], [2., self.screen_height*40]]
        sigma = [[100, 0], [0, 100]]
        motion_sigma = 20.
        self.robot = Robot(mu, sigma, motion_uncertainty=motion_sigma, size=self.robot_size)
        self.outline = 2

    def start(self):
        pg.init()
        self.screen.fill('black')

        while True:
            self.drawgrid()
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
                    else:
                        motion = False
                    if motion:
                        self.robot.move(motion)
                        print(f'sigmax= {self.robot.sigma[0][0]} sigmay={self.robot.sigma[1][1]}')
                    if event.key == pg.K_m:
                        self.robot.measure()
            pg.display.flip()

    def drawgrid(self):

        rect = pg.Rect(self.panel_width, 0, self.screen_width, self.screen_height)
        pg.draw.rect(self.screen, (200, 200, 200), rect, 0)

        gauss = self.gauss2surface(self.robot.pos, self.robot.sigma)
        gauss = pg.transform.smoothscale(gauss, (self.plot_width, self.plot_height))
        self.screen.blit(gauss, (self.panel_width, 0))
        self.screen.blit(self.robot_img, [(self.panel_width+self.robot.pos[0])-self.robot.size//2, self.robot.pos[1]-(self.robot.size//2)])

        plt.close()

    def gauss2surface(self, mu, sigma):
        scale = 100
        x, y = np.mgrid[0:self.screen_width//scale:1, self.screen_height//scale:0:-1]
        pos = np.dstack((x, y))
        rv = multivariate_normal(np.array(mu)/scale, np.array(sigma)/scale)
        z = rv.pdf(pos)
        plt.figure(figsize=self.figsize)
        fig = plt.gcf()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.invert_yaxis()
        # ax.set_axis_off()
        # levels = [0.0000005, 0.000001, 0.00001, 0.0001, 0.0002, 0.00025]
        cs = ax.contourf(x, y, z, levels=5, cmap='coolwarm')
        ax.contour(cs, colors='k')

        # Major ticks every 20, minor ticks every 5
        x_ticks = np.arange(0, self.screen_width//scale, (self.screen_width//scale)/20)
        y_ticks = np.arange(0, self.screen_height//scale, (self.screen_height//scale)/20)

        ax.set_xticks(x_ticks)
        ax.set_yticks(y_ticks)

        # And a corresponding grid
        ax.grid(which='both', c='k', ls='-', alpha=0.3)
        return utils.fig2surface(fig)



import matplotlib.pyplot as plt
import numpy as np

# Data to plot.
# x, y = np.meshgrid(np.arange(7), np.arange(10))
# z = np.sin(0.5 * x) * np.cos(0.52 * y)
#
# x, y = np.mgrid[-10:10:.1, -10:10:.1]
# rv = multivariate_normal([0, 0], [[2.0, 2.], [2., 2.5]])
# pos = np.dstack((x, y))
# z = rv.pdf(pos)
# fig = plt.gcf()
# ax = fig.add_axes([0, 0, 1, 1])
# # ax.set_axis_off()
# cs = ax.contourf(x, y, z, levels=4, cmap='coolwarm')
# ax.contour(cs, colors='k')

# print(get_dpi())

# plt.show()
kf = Kalman_2D()
kf.start()