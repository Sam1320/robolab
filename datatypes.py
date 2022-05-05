import sys

import pygame as pg
import matplotlib.pyplot as plt
import random
import math


import utils


class RobotDiff:
    def __init__(self, world_size=(100, 100), state=None, forward_noise=0, turning_noise=0, sense_noise=0, image=None):
        if not state:
            self.x = random.random()*world_size[0]
            self.y = random.random()*world_size[1]
            self.orientation = random.random() * 2 * math.pi
        else:
            self.x = state[0]
            self.y = state[1]
            self.orientation = state[2]

        self.forward_noise = forward_noise
        self.turning_noise = turning_noise
        self.sense_noise = sense_noise

        self.image_original = image
        if self.image_original:
            self.image = pg.transform.rotozoom(self.image_original, math.degrees(self.orientation), 1)

    def get_position(self):
        return self.x, self.y

    def move(self, linear_v, angular_v):
        dt = 1
        linear_v = random.gauss(linear_v, self.forward_noise)
        angular_v = random.gauss(angular_v, self.turning_noise)

        self.x += (linear_v*dt)*math.cos(self.orientation)
        self.y += (linear_v*dt)*math.sin(self.orientation)
        self.orientation += angular_v*dt

        if self.image_original:
            self.image = pg.transform.rotozoom(self.image_original, math.degrees(self.orientation), 1)

    def sense(self, landmarks):
        Z = []
        for i, landmark in enumerate(landmarks):
            dist = math.sqrt((self.x - landmarks[i][0]) ** 2 + (self.y - landmarks[i][1]) ** 2)
            dist = random.gauss(dist, self.sense_noise)
            Z.append(dist)
        return Z

    def measurement_prob(self, Z, landmarks):
        # calculates how likely a measurement should be
        prob = 1.0
        for i in range(len(landmarks)):
            dist = math.sqrt((self.x - landmarks[i][0]) ** 2 + (self.y - landmarks[i][1]) ** 2)
            prob *= utils.Gaussian(dist, self.sense_noise, Z[i])
        return prob


class RobotGUI:
    def __init__(self, robot_type='diff', robot_img='robot_ship', screen_width=1500, height_width_ratio=2/3, font_size=0):
        self.height_width_ratio = height_width_ratio
        self.screen_width = screen_width
        self.screen_height = screen_width*self.height_width_ratio
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height), pg.DOUBLEBUF)
        input_width = font_size * 2
        label_width = font_size * 8
        self.panel_width = input_width * label_width
        self.panel_height = self.screen_height
        self.plot_width = self.screen_width - self.panel_width
        self.plot_height = self.screen_height

        # robot stuff
        self.world_size = (100, int(100*self.height_width_ratio))
        self.robot_size = self.screen_width//30
        robot_img = pg.transform.smoothscale(pg.image.load(f'{robot_img}.png').convert_alpha(), (self.robot_size, self.robot_size))
        robot_img = pg.transform.rotozoom(robot_img, -90, 1)
        self.robot = RobotDiff(world_size=self.world_size, image=robot_img) if robot_type == 'diff' else None
        # plot stuff
        self.dpi = utils.get_dpi()

        self.figsize = (int(self.plot_width/self.dpi), int(self.plot_height/self.dpi))


    def start(self):
        pg.init()
        clock = pg.time.Clock()
        self.screen.fill('black')
        while 1:
            self.draw()
            self.handle_events()
            clock.tick(30)
            print(clock.get_fps())
            pg.display.flip()

    def draw(self):
        plot = pg.transform.smoothscale(self.plot2surface(), (self.plot_width, self.plot_height))
        self.screen.blit(plot, (self.panel_width, 0))
        robotx, roboty = self.robot.get_position()
        robotx_screen, roboty_screen = self.world2screen((robotx, roboty))
        # center of the robot should coincide with center of the image instead of the upper left corner
        frame = self.robot.image.get_rect()
        frame.center = robotx_screen, roboty_screen
        pg.draw.rect(self.screen, (0, 0, 0), frame, 1)
        self.screen.blit(self.robot.image, frame)

    def handle_events(self):
        pass

    def plot2surface(self):
        plt.figure(figsize=self.figsize)
        fig = plt.gcf()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.plot()
        ax.grid()
        plt.close()
        return utils.fig2surface(fig)

    def world2screen(self, pos):
        x, y = pos[0], self.world_size[1]-pos[1]
        x_norm = x/self.world_size[0]
        y_norm = y/self.world_size[1]
        new_y = self.screen_height*y_norm
        new_x = self.screen_width*x_norm
        new_x += self.panel_width
        return new_x, new_y

if __name__ == "__main__":
    gui = RobotGUI()
    gui.start()