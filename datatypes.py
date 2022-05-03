import sys

import pygame as pg
import matplotlib.pyplot as plt
import random
import math

import utils


class RobotDiff:
    def __init__(self, world_size, landmarks=None, image=None):
        self.x = random.random()*world_size[0]
        self.y = random.random()*world_size[1]
        self.orientation = random.random()*2*math.pi
        self.forward_noise = 0
        self.turning_noise = 0
        self.sense_noise = 0
        self.landmarks = landmarks
        self.image_original = image
        self.image = pg.transform.rotozoom(self.image_original, math.degrees(self.orientation), 1)

    def get_state(self):
        return self.x, self.y, self.orientation

    def move(self, linear_v, angular_v):
        dt = 1
        self.x += (linear_v*dt)*math.cos(self.orientation)
        self.y += (linear_v*dt)*math.sin(self.orientation)
        self.orientation += angular_v*dt
        if self.image_original:
            self.image = pg.transform.rotozoom(self.image_original, math.degrees(self.orientation), 1)

    def sense(self, landmarks):
        return self.x, self.y, self.orientation


class RobotGUI:
    def __init__(self, robot_type='diff', robot_img='robot_ship', screen_width=1500, font_size=0):
        self.height_width_ratio = 2/3
        self.screen_width = screen_width
        self.screen_height = screen_width*self.height_width_ratio
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
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
        self.plot = pg.transform.smoothscale(self.plot2surface(), (self.plot_width, self.plot_height))

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
        self.screen.blit(self.plot, (self.panel_width, 0))
        robotx, roboty, orientation = self.robot.get_state()
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
        x, y = pos[0], (self.world_size[1]-pos[1])
        x_norm = x/self.world_size[0]
        y_norm = y/self.world_size[1]
        new_y = self.screen_height*y_norm
        new_x = self.screen_width*x_norm
        new_x += self.panel_width
        return new_x, new_y