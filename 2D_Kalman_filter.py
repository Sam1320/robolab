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
    def __init__(self, true_position, position_uncertainty, size):
        self.pos = true_position
        self.mu = true_position
        self.sigma = position_uncertainty
        self.size = size

class Kalman_2D:
    def __init__(self, screen_width=2000, font_size=0):
        self.screen_width = screen_width
        self.screen_height = screen_width//2
        input_width = font_size * 2
        input_height = font_size * 1.5
        label_width = font_size * 8
        label_height = font_size * 1.5
        self.dpi = dpi

        self.panel_width = input_width + label_width

        self.plot_width = self.screen_width - self.panel_width
        self.plot_height = self.screen_height
        self.font_size = font_size
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        robot_x = random.randint(0, self.screen_width-1)
        robot_y = random.randint(0, self.screen_height-1)
        mu = [robot_x, robot_y]
        sigma = [[(self.screen_width+self.panel_width)*40, 2.], [2., self.screen_height*40]]
        self.robot = Robot(mu, sigma, size=self.screen_width/20)
        self.cell_width = self.robot.size*1.2
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
            pg.display.flip()

    def drawgrid(self):
        robot = pg.image.load('robot2.png')
        robot = pg.transform.smoothscale(robot, (self.robot.size, self.robot.size))
        rect = pg.Rect(self.panel_width, 0, self.screen_width, self.screen_height)
        pg.draw.rect(self.screen, (200, 200, 200), rect, 0)

        gauss = self.gauss2surface(self.robot.pos, self.robot.sigma)
        gauss = pg.transform.smoothscale(gauss, (self.plot_width, self.plot_height))
        self.screen.blit(gauss, (self.panel_width, 0))
        self.screen.blit(robot, [(self.panel_width+self.robot.pos[0])-self.robot.size//2, self.robot.pos[1]-(self.robot.size//2)])

        plt.close()

    def gauss2surface(self, mu, sigma):
        scale = 10
        x, y = np.mgrid[0:self.screen_width//scale:1/scale, self.screen_height//scale:0:-1/scale]
        pos = np.dstack((x, y))
        rv = multivariate_normal(np.array(mu)/scale, np.array(sigma)/scale)
        z = rv.pdf(pos)
        s = (int(self.plot_width/self.dpi), int(self.plot_height/self.dpi))
        plt.figure(figsize=s)
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