import sys

import pygame as pg
import random
import math

import utils


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
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height), pg.DOUBLEBUF)
        input_width = font_size * 2
        label_width = font_size * 8
        self.panel_width = input_width * label_width
        self.panel_height = self.screen_height
        self.window_width = self.screen_width - self.panel_width
        self.window_height = self.screen_height

        # robot stuff
        self.world_size = (100, int(100*self.height_width_ratio))
        self.robot_size = self.screen_width//30
        robot_img = pg.transform.smoothscale(pg.image.load(f'{robot_img}.png').convert_alpha(), (self.robot_size, self.robot_size))
        robot_img = pg.transform.rotozoom(robot_img, -90, 1)
        self.robot = RobotParticle(world_size=self.world_size, image=robot_img) if robot_type == 'diff' else None
        # plot stuff
        self.dpi = utils.get_dpi()
        self.figsize = (int(self.window_width / self.dpi), int(self.window_height / self.dpi))


    def start(self):
        pg.init()
        clock = pg.time.Clock()
        self.screen.fill('black')
        while 1:
            self.draw()
            self.handle_events()
            clock.tick(30)
            # print(clock.get_fps())
            pg.display.flip()

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
