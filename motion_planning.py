import pickle
import random
import sys
import pygame as pg
from datatypes import RobotGUI
import utils

#TODO
# choose better arrow and start icons (sharper edges)
# generate grid at random
# add interface to specify grid size

# DONE: add button to save grid


class MotionPlanningGUI(RobotGUI):
    def __init__(self, world_size=(20, 10), load_grid=True):
        self.world_size = world_size
        if load_grid:
            with open('grid.pickle', 'rb') as file:
                self.grid = pickle.load(file)
                self.world_size = len(self.grid[1]), len(self.grid[0])
        else:
            self.grid = [[0 if random.random() < 1. else 1 for row in range(self.world_size[0])] for col in range(self.world_size[1])]
        scale = int((1/world_size[0])*900)
        self.window_width = scale * world_size[0]
        self.window_height = scale * world_size[1]
        self.grid_colors = {'free': (200, 200, 200), 'obstacle': (50, 50, 50)}
        self.screen = pg.display.set_mode((self.window_width, self.window_height), pg.DOUBLEBUF)
        arrow_img = pg.transform.smoothscale(pg.image.load('arrow.png'), (scale/2, scale/2))
        goal_img = pg.transform.smoothscale(pg.image.load('goal.png'), (scale/2, scale/2))
        start_img = pg.transform.smoothscale(pg.image.load('start.png'), (scale/2, scale/2))
        exclamation_img = pg.transform.smoothscale(pg.image.load('exclamation.png'), (scale/2, scale/2))
        self.arrows = {
            '^': pg.transform.rotozoom(arrow_img, 90, 1),
            '>': pg.transform.rotozoom(arrow_img, 0, 1),
            'v': pg.transform.rotozoom(arrow_img, -90, 1),
            '<': pg.transform.rotozoom(arrow_img, 180, 1),
            '*': goal_img,
            '!': exclamation_img,
            'start': start_img
        }
        # self.grid = [[0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        #              [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        #              [1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        #              [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        #              [0, 1, 0, 0, 1, 1, 1, 1, 0, 0],
        #              [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        #              [0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
        #              [0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
        #              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #              [0, 1, 0, 0, 0, 1, 1, 1, 0, 0]]
        self.goal = None
        self.start_pos = None
        self.cell_size = scale
        self.outline_thickness = 2
        self.path = [[' ' for col in range(self.world_size[0])] for row in range(self.world_size[1])]

    def draw(self):
        for row, y in enumerate(range(0, self.window_height, self.cell_size)):
            for col, x in enumerate(range(0, self.window_width, self.cell_size)):
                rect = pg.Rect(x + self.outline_thickness, y + self.outline_thickness, self.cell_size - self.outline_thickness,
                               self.cell_size - self.outline_thickness)
                cell_color = self.grid_colors['obstacle'] if self.grid[row][col] else self.grid_colors['free']
                pg.draw.rect(self.screen, cell_color, rect, 0)
                policy = self.path[row][col]
                if self.start_pos == [row, col]:
                    self.screen.blit(self.arrows['start'], (x+self.cell_size/4, y+self.cell_size/4))
                elif policy != ' ':
                    self.screen.blit(self.arrows[policy], (x+self.cell_size/4, y+self.cell_size/4))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONUP:
                state = event.button
                match state:
                    case 1:
                        pos = pg.mouse.get_pos()
                        self.start_pos = list(self.coords_to_row_col(pos[0], pos[1]))
                    case 2:
                        pos = pg.mouse.get_pos()
                        obstacle = list(self.coords_to_row_col(pos[0], pos[1]))
                        self.grid[obstacle[0]][obstacle[1]] = (self.grid[obstacle[0]][obstacle[1]] + 1) % 2
                    case 3:
                        pos = pg.mouse.get_pos()
                        self.goal = list(self.coords_to_row_col(pos[0], pos[1]))
                if self.start_pos and self.goal:
                    self.path = utils.search(self.grid, self.start_pos, self.goal, utils.heuristic)
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    with open('grid.pickle', 'wb') as file:
                        pickle.dump(self.grid, file)
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


if __name__ == "__main__":
    motiongui = MotionPlanningGUI()
    motiongui.start()

