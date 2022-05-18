import os.path
import sys

import pygame as pg
import random
import math
import numpy as np
import env
import utils

#TODO:
# get rid of panels (replaced by a start window for adjusting settings)

#DONE: get rid of get_dpi() and find better alternative

class RobotGrid:
    def __init__(self, world_size=(100, 100)):
        self.x = int(random.random()*world_size[0])
        self.y = int(random.random()*world_size[1])
        self.world_size = world_size

    def move(self, dx, dy):
        self.x = (self.x+dx) % self.world_size[0]
        self.y = (self.y+dy) % self.world_size[1]

class RobotKalman2D():
    def __init__(self, true_position, position_uncertainty, motion_uncertainty, measurement_uncertainty, size):
        self.pos = true_position
        self.mu = list(true_position)
        self.sigma = position_uncertainty
        self.measurement_sigma = measurement_uncertainty
        self.motion_sigma = motion_uncertainty
        self.size = size

    def move(self, motion):
        # motion update. Predict new position and variance.
        if motion[0]:
            self.mu[0] += motion[0]
            self.sigma[0][0] = np.sqrt(self.sigma[0][0]**2 + self.motion_sigma**2)
            self.pos[0] += np.random.normal(motion[0], self.motion_sigma)
        elif motion[1]:
            self.mu[1] += motion[1]
            self.sigma[1][1] = np.sqrt(self.sigma[1][1]**2 + self.motion_sigma**2)
            self.pos[1] += np.random.normal(motion[1], self.motion_sigma)

    def sense(self):
        measurement = np.random.multivariate_normal(self.pos, self.measurement_sigma, 1)[0]
        self.mu[0] = (self.mu[0]*(self.measurement_sigma[0][0]**2) + measurement[0]*self.sigma[0][0]**2)/ (self.sigma[0][0]**2+self.measurement_sigma[0][0]**2)
        self.mu[1] = (self.mu[1]*(self.measurement_sigma[1][1]**2) + measurement[1]*self.sigma[1][1]**2)/ (self.sigma[1][1]**2+self.measurement_sigma[1][1]**2)
        self.sigma[0][0] = np.sqrt(1/(1/self.sigma[0][0]**2 + 1/self.measurement_sigma[0][0]**2))
        self.sigma[1][1] = np.sqrt(1/(1/self.sigma[1][1]**2 + 1/self.measurement_sigma[0][0]**2))

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
    def __init__(self, robot_type='diff', robot_img='robot_ship', screen_width=1500, height_width_ratio=2/3):
        self.height_width_ratio = height_width_ratio
        self.screen_width = screen_width
        self.screen_height = int(screen_width*self.height_width_ratio)

        # robot stuff
        self.world_size = (100, int(100*self.height_width_ratio))
        self.robot_size = self.screen_width//30
        self.robot_img = robot_img
        self.robot_type = robot_type

        # plot stuff
        self.dpi = utils.get_dpi()
        self.figsize = (int(self.screen_width / self.dpi), int(self.screen_height / self.dpi))

    def init_pygame(self):
        """ Initialize display, transform and load images."""
        pass

    def start(self, verbose=True, fps=30):
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
        return new_x, new_y
