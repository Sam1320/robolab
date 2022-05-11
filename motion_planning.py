import sys
import pygame as pg
from datatypes import RobotGUI
import utils


class MotionPlanningGUI(RobotGUI):
    def __init__(self, world_size=(10, 10)):
        scale = int((1/world_size[0])*700)
        self.window_width = scale * world_size[0]
        self.window_height = scale * world_size[1]
        self.grid_colors = {'free': (200, 200, 200), 'obstacle': (50, 50, 50)}
        # self.grid = [[0 for row in range(self.world_size[0])] for col in range(self.world_size[1])]
        # self.grid[1][1] = 1-
        self.screen = pg.display.set_mode((self.window_width, self.window_height), pg.DOUBLEBUF)
        self.world_size = world_size
        arrow_img = pg.transform.smoothscale(pg.image.load('arrow.png'), (scale/2, scale/2))
        goal_img = pg.transform.smoothscale(pg.image.load('goal.png'), (scale/2, scale/2))
        self.arrows = {
                       '^': pg.transform.rotozoom(arrow_img, 90, 1),
                       '>': pg.transform.rotozoom(arrow_img, 0, 1),
                       'v': pg.transform.rotozoom(arrow_img, -90, 1),
                       '<': pg.transform.rotozoom(arrow_img, 180, 1),
                        '*': goal_img
                       }
        self.grid = [[0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                     [1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]]
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
                if policy != ' ':
                    self.screen.blit(self.arrows[policy], (x+20, y+20))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONUP:
                pos = list(pg.mouse.get_pos())
                goal = list(self.coords_to_row_col(pos[0], pos[1]))
                self.path = utils.search(self.grid, [0, 0], goal, utils.heuristic)


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
        if not row or not col:
            raise Exception('Bad click coordinate')
        return row, col


if __name__ == "__main__":
    motiongui = MotionPlanningGUI()
    # path = utils.search(motiongui.grid, [0, 0,])
    motiongui.start()

