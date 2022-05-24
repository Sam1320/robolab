import os.path
import pickle
import sys
from tkinter import messagebox

import pygame as pg
import random
import math
import numpy as np
import env
from src import utils


class RobotGrid:
    def __init__(self, world_size=(100, 100)):
        self.x = int(random.random()*world_size[0])
        self.y = int(random.random()*world_size[1])
        self.world_size = world_size

    def move(self, dx, dy):
        self.x = (self.x+dx) % self.world_size[0]
        self.y = (self.y+dy) % self.world_size[1]


class RobotKalman1D():
    def __init__(self, true_position, position_uncertainty, motion_uncertainty, measurement_uncertainty, size):
        self.pos = true_position
        self.mu = true_position
        self.sigma = position_uncertainty
        self.measurement_sigma = measurement_uncertainty
        self.motion_sigma = motion_uncertainty
        self.size = size

    def move(self, motion):
        # motion update. Predict new position and variance.
        self.mu += motion
        self.sigma = np.sqrt(self.sigma**2 + self.motion_sigma**2)
        self.pos += np.random.normal(motion, self.motion_sigma)

    def sense(self):
        measurement = np.random.normal(self.pos, self.measurement_sigma, 1)[0]
        self.mu = (self.mu*(self.measurement_sigma**2) + measurement*self.sigma**2)/ (self.sigma**2+self.measurement_sigma**2)
        self.sigma = np.sqrt(1/(1/self.sigma**2 + 1/self.measurement_sigma**2))


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


class GridGUI(RobotGUI):
    def __init__(self, world_size=(10, 6), load_grid=False, obstacle_prob=0.2):
        self.world_size = world_size
        if load_grid:
            with open('grid.pickle', 'rb') as file:
                self.grid_obstacles = pickle.load(file)
                self.world_size = len(self.grid_obstacles[0]), len(self.grid_obstacles)
        else:
            self.grid_obstacles = [[1 if random.random() < obstacle_prob else 0 for row in range(self.world_size[0])] for col in range(self.world_size[1])]
        # as the grid gets bigger the cells get smaller
        self.scale = int((1/(world_size[0]+world_size[1]))*1200)
        self.window_width = self.scale * self.world_size[0]
        self.window_height = self.scale * self.world_size[1]
        self.grid_colors = {'free': (200, 200, 200), 'obstacle': (50, 50, 50)}

        self.goal = None
        self.start_pos = None
        self.cell_size = self.scale
        self.outline_thickness = 1
        self.grid_state = [[' ' for col in range(self.world_size[0])] for row in range(self.world_size[1])]

    def init_pygame(self):
        img_size = self.scale/2
        self.screen = pg.display.set_mode((self.window_width, self.window_height), pg.DOUBLEBUF)
        self.screen.fill('black')
        arrow_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, 'arrow.png')), (img_size, img_size))
        goal_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, 'flag.png')), (img_size, img_size))
        start_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, 'robot2.png')), (img_size, img_size))
        exclamation_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, 'exclamation.png')), (img_size, img_size))
        self.images = {
            '^': pg.transform.rotozoom(arrow_img, 90, 1),
            '>': pg.transform.rotozoom(arrow_img, 0, 1),
            'v': pg.transform.rotozoom(arrow_img, -90, 1),
            '<': pg.transform.rotozoom(arrow_img, 180, 1),
            '*': goal_img,
            '!': exclamation_img,
            'start': start_img
        }

    def draw(self):
        for row, y in enumerate(range(0, self.window_height, self.cell_size)):
            for col, x in enumerate(range(0, self.window_width, self.cell_size)):
                rect = pg.Rect(x + self.outline_thickness, y + self.outline_thickness, self.cell_size - self.outline_thickness,
                               self.cell_size - self.outline_thickness)
                #TODO: encode obstacles inside grid state
                cell_color = self.grid_colors['obstacle'] if self.grid_obstacles[row][col] else self.grid_colors['free']
                pg.draw.rect(self.screen, cell_color, rect, 0)
                policy = self.grid_state[row][col]
                if self.start_pos == [row, col]:
                    self.screen.blit(self.images['start'], (x + self.cell_size / 4, y + self.cell_size / 4))
                if policy != ' ':
                    self.screen.blit(self.images[policy], (x + self.cell_size / 4, y + self.cell_size / 4))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 1
            elif event.type == pg.MOUSEBUTTONUP:
                state = event.button
                match state:
                    case 1:
                        self.handle_left_click()
                    case 2:
                        self.handle_middle_click()
                    case 3:
                        self.handle_right_click()
                self.update_grid_state()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.handle_enter()
                elif event.key == pg.K_ESCAPE:
                    return 1
        return 0

    def handle_enter(self):
        messagebox.showinfo(title='Info', message='Map saved')
        with open('grid.pickle', 'wb') as file:
            pickle.dump(self.grid_obstacles, file)

    def update_grid_state(self):
        pass

    def handle_left_click(self):
        pass

    def handle_middle_click(self):
        pos = pg.mouse.get_pos()
        obstacle = list(self.coords_to_row_col(pos[0], pos[1]))
        self.grid_obstacles[obstacle[0]][obstacle[1]] = (self.grid_obstacles[obstacle[0]][obstacle[1]] + 1) % 2

    def handle_right_click(self):
        pos = pg.mouse.get_pos()
        if self.goal:
            self.grid_state[self.goal[0]][self.goal[1]] = ' '
        self.goal = list(self.coords_to_row_col(pos[0], pos[1]))
        self.grid_state[self.goal[0]][self.goal[1]] = '*'

    def coords_to_row_col(self, x, y):
        """Converts x y coordinates to col and row numbers."""
        row, col = None, None
        for i in range(self.world_size[1]):
            if y < self.cell_size*(i+1):
                row = i
                break
        for i in range(self.world_size[0]):
            if x < self.cell_size*(i+1):
                col = i
                break
        if row is None or col is None:
            raise Exception('Bad click coordinate')
        return row, col
