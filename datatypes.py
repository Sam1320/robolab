import os.path
import sys

import pygame as pg
import random
import math

import env
import utils

#TODO:
# get rid of panels (replaced by a start window for adjusting settings)
# get rid of get_dpi() and find better alternative

class RobotGrid:
    def __init__(self, world_size=(100, 100)):
        self.x = int(random.random()*world_size[0])
        self.y = int(random.random()*world_size[1])
        self.world_size = world_size

    def move(self, dx, dy):
        self.x = (self.x+dx) % self.world_size[0]
        self.y = (self.y+dy) % self.world_size[1]


class RobotParticle:
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
        self.screen_height = int(screen_width*self.height_width_ratio)
        input_width = font_size * 2
        label_width = font_size * 8
        self.panel_width = input_width * label_width
        self.panel_height = self.screen_height
        self.window_width = self.screen_width - self.panel_width
        self.window_height = self.screen_height

        # robot stuff
        self.world_size = (100, int(100*self.height_width_ratio))
        self.robot_size = self.screen_width//30
        self.robot_img = robot_img
        self.robot_type = robot_type

        # plot stuff
        self.dpi = 93 #utils.get_dpi()
        self.figsize = (int(self.window_width / self.dpi), int(self.window_height / self.dpi))

    def init_pygame(self):
        """ Initialize display, transform and load images."""
        pass

    def start(self, verbose=False, fps=30):
        self.init_pygame()
        clock = pg.time.Clock()
        while 1:
            self.draw()
            end_game = self.handle_events()
            clock.tick(fps)
            if verbose:
                print(clock.get_fps())
            pg.display.flip()
            if end_game:
                return 1


    def draw(self):
        pass

    def handle_events(self):
        pass

    def world2screen(self, pos):
        x, y = pos[0], self.world_size[1]-pos[1]
        x_norm = x/self.world_size[0]
        y_norm = y/self.world_size[1]
        new_y = self.screen_height*y_norm
        new_x = self.screen_width*x_norm
        new_x += self.panel_width
        return new_x, new_y
