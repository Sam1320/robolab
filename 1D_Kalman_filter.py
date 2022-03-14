import sys

import math
import pygame as pg
import matplotlib.pyplot as plt
import utils
import numpy as np

grid_width = 20
cell_width = int((1/grid_width)*1000)
win_width = grid_width*cell_width
outline = 2

plot_height = cell_width*10
plot_width = win_width
robot_size = int(cell_width/2)
robot_x = 1

mu = robot_x
sigma = 20

motion_sigma = 0.2
measurement_sigma = 1.

constant_shift = 0.5
step_size = 10


def main():
    global screen, robot_x, mu, sigma
    pg.init()
    screen = pg.display.set_mode((win_width, cell_width+plot_height))
    screen.fill('black')

    while True:
        drawgrid2()
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    action = -1 * step_size
                elif event.key == pg.K_RIGHT:
                    action = 1 * step_size
                else:
                    action = False
                if action:
                    mu, sigma = motion_update(mu, sigma, action)
                    true_move = np.random.normal(action, motion_sigma, 1)[0]
                    robot_x = (robot_x + true_move)
                    # bound movements to grid limits
                    robot_x = max(min(grid_width-1, robot_x), 0)
                if event.key == pg.K_m:
                    measurement = np.random.normal(robot_x, measurement_sigma, 1)[0]
                    # print(f'z = {measurement} truth = {robot_x}')
                    mu, sigma = measurement_update(mu, sigma, measurement)

                print(f"estimate = {mu}, truth = {robot_x}")
                print(f'error = {abs(mu-robot_x)}')
                print('----'*20)
        pg.display.flip()


def drawgrid():
    robot = pg.image.load('robotic.png')
    robot = pg.transform.smoothscale(robot, (robot_size, robot_size))
    y = plot_height
    for col, x in enumerate(range(0, win_width, cell_width)):
        rect = pg.Rect(x+outline, y+outline, cell_width-outline, cell_width-outline)
        pg.draw.rect(screen, (255, 255, 255), rect, 0)
        if col == robot_x:
            screen.blit(robot, [x+cell_width/4, y+cell_width/4])
    gauss = gauss2surface(mu, sigma)
    gauss = pg.transform.smoothscale(gauss, (plot_width, plot_height))
    screen.blit(gauss, [0, 0, plot_width, plot_height])
    plt.close()

def drawgrid2():
    robot = pg.image.load('robotic.png')
    robot = pg.transform.smoothscale(robot, (robot_size, robot_size))
    y = plot_height

    rect = pg.Rect(outline, y+outline, win_width - outline, cell_width - outline)
    pg.draw.rect(screen, (255, 255, 255), rect, 0)

    screen.blit(robot, [robot_x + cell_width / 4, y + cell_width / 4])

    gauss = gauss2surface(mu, sigma)
    gauss = pg.transform.smoothscale(gauss, (plot_width, plot_height))
    screen.blit(gauss, [0, 0, plot_width, plot_height])
    plt.close()


def motion_update(mu, sigma, action):
    new_mu = mu + action
    new_sigma = sigma + motion_sigma
    return new_mu, new_sigma


def measurement_update(mu, sigma, mu2):
    new_mu = (mu*measurement_sigma**2 + mu2*sigma**2) / (sigma**2+measurement_sigma**2)
    new_sigma = 1/(1/sigma**2 + 1/measurement_sigma**2)
    return new_mu, new_sigma


def gaussian(x, mu, sigma):
    return 1/(np.sqrt(2*np.pi*sigma**2))*np.exp(-0.5*(((x-mu)**2)/sigma**2))


def gauss2surface(mu, sigma):
    x = np.linspace(0, 20, 200)
    plt.figure(figsize=(10, 5))
    fig = plt.gcf()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    plt.xlim(0, 20)
    plt.ylim(0, 1)
    plt.plot(x, gaussian(x, mu+constant_shift, sigma), color='blue')

    surface = utils.fig2surface(fig)
    return surface


main()