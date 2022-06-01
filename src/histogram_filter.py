import random
import sys

import pygame as pg
import matplotlib.pyplot as plt
import numpy as np
import os


from src import utils
import env
from src.datatypes import GridGUI, RobotGrid


class HistogramFilterGUI(GridGUI):
    def __init__(self, world_size=(10, 6), load_grid=False, obstacle_prob=0.2, path_arrows=True, robot_size='small',
                pHit=0.6, pMiss=0.2, pOvershoot=0.1, pUndershoot=0.1, pGood=0.8):
        super().__init__(world_size=world_size, load_grid=load_grid, obstacle_prob=obstacle_prob,
                         path_arrows=path_arrows, plot=True, robot_size=robot_size)
        # robot motion and sensing probabilities
        self.pHit = pHit
        self.pMiss = pMiss
        self.pGood = pGood
        self.pOvershoot = pOvershoot
        self.pUndershoot = pUndershoot

        # grid variables
        self.grid_state = [[random.sample(['green', 'red'], 1)[0] for _ in range(world_size[0])] for _ in range(world_size[1])]
        self.grid_colors = {'green': (128, 255, 128), 'red': (255, 150, 70), 'white': (200, 200, 200), 'black': (0, 0, 0)}
        self.probs = [[1/(world_size[0]*world_size[1]) for _ in range(world_size[0])] for _ in range(world_size[1])]

        # constant values for the histogram
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        self.ax = ax
        self.fig = fig
        x = np.arange(1, world_size[0] + 1)
        y = np.arange(world_size[1], 0, -1)
        xv, yv = np.meshgrid(x, y)
        xv, yv = xv.flatten(), yv.flatten()
        self.xv = xv
        self.yv = yv

    def init_pygame(self):
        self.screen = pg.display.set_mode((self.window_width*2, self.window_height))
        self.robot = RobotGrid(world_size=self.world_size)
        self.robot_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, self.robot_img)), (self.cell_size, self.cell_size))

    def handle_events(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    motion = (-1, 0)
                elif event.key == pg.K_RIGHT:
                    motion = (1, 0)
                elif event.key == pg.K_DOWN:
                    motion = (0, 1)
                elif event.key == pg.K_UP:
                    motion = (0, -1)
                elif event.key == pg.K_ESCAPE:
                    return 1
                else:
                    motion = None
                if motion:
                    if not random.random() < self.pGood:
                        overShoot = random.random() < self.pOvershoot
                        if overShoot:
                            motion = (2 * motion[0], 2 * motion[1])
                        else:
                            motion = (0, 0)

                    self.robot.move(motion[0], motion[1])
                    self.probs = self.motion_update(self.probs, motion)
                if event.key == pg.K_s:
                    good_measurement = random.random() < self.pHit
                    measurement = self.grid_state[self.robot.y][self.robot.x] if good_measurement else ('green' if self.grid_state[0][self.robot.x] == 'red' else 'red')
                    self.probs = self.measurement_update(self.probs, measurement)

        return 0

    def draw(self):
        self.screen.fill('black')
        for row, y in enumerate(range(0, self.window_height, self.cell_size)):
            for col, x in enumerate(range(0, self.window_width, self.cell_size)):
                rect = pg.Rect(x + self.outline_thickness, y + self.outline_thickness, self.cell_size - self.outline_thickness,
                               self.cell_size - self.outline_thickness)
                pg.draw.rect(self.screen, self.grid_colors[self.grid_state[row][col]], rect, 0)
                if row == self.robot.y and col == self.robot.x:
                    self.screen.blit(self.robot_img, (x, y))
        histogram = self.plot2surface(self.probs)
        histogram = pg.transform.smoothscale(histogram, (self.window_width, self.window_height))
        self.screen.blit(histogram, (self.window_width, self.outline_thickness))

    def motion_update(self, probs, motion):
        new_p = [[0 for _ in range(len(probs[0]))] for _ in range(len(probs))]
        for i in range(len(probs)):
            for j in range(len(probs[0])):
                # apply law of total probability. i.e. sum over all possible transitions
                t1 = self.pGood * probs[(i - motion[1]) % self.world_size[1]][(j - motion[0]) % self.world_size[0]]  # the robot moved correctly
                t2 = self.pOvershoot * probs[(i - 2 * motion[1]) % self.world_size[1]][
                    (j - 2 * motion[0]) % self.world_size[0]]  # the robot moved too much
                t3 = self.pUndershoot * probs[i][j]  # the robot did not move
                new_p[i][j] = round(t1 + t2 + t3, 4)
        total_sum = sum([sum(row) for row in new_p]) + 1e-10
        new_p = [[round(p / total_sum, 4) for p in row] for row in new_p]
        return new_p

    def measurement_update(self, probs, measurement):
        new_p = [[0 for _ in range(len(probs[0]))] for _ in range(len(probs))]
        for i in range(len(probs)):
            for j in range(len(probs[0])):
                hit = measurement == self.grid_state[i][j]
                # apply bayes rule
                new_p[i][j] = probs[i][j] * (hit * self.pHit + (1 - hit) * self.pMiss)
        # normalize
        total_sum = sum([sum(row) for row in new_p]) + 1e-10
        new_p = [[round(p / total_sum, 4) for p in row] for row in new_p]
        return new_p

    def plot2surface(self, probs):
        weights = np.array(probs).flatten()
        hist = self.ax.hist2d(self.xv, self.yv, bins=self.world_size, weights=weights, cmap=plt.cm.jet)
        surface = utils.fig2surface(self.fig)
        plt.close(self.fig)
        hist[-1].remove()
        return surface


if __name__ == "__main__":
    gui = HistogramFilterGUI()
    gui.start(verbose=False)