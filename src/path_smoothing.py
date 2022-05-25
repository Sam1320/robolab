import pygame as pg
from src.datatypes import GridGUI
from src import utils
from copy import deepcopy


class PathSmoothingGUI(GridGUI):
    def __int__(self, world_size=(10, 6), load_grid=False, obstacle_prob=0.2):
        super().__init__(world_size=world_size, load_grid=load_grid, obstacle_prob=obstacle_prob)

    def handle_left_click(self):
        pos = pg.mouse.get_pos()
        self.start_pos = list(self.coords_to_row_col(pos[0], pos[1]))

    def update_grid_state(self):
        if self.start_pos and self.goal:
            self.grid_state, self.path_coords = utils.a_star_search(self.grid_obstacles, self.start_pos, self.goal, utils.heuristic)

    def draw(self):
        for row, y in enumerate(range(0, self.window_height, self.cell_size)):
            for col, x in enumerate(range(0, self.window_width, self.cell_size)):
                rect = pg.Rect(x + self.outline_thickness, y + self.outline_thickness, self.cell_size - self.outline_thickness,
                               self.cell_size - self.outline_thickness)
                #TODO: encode obstacles inside grid state
                cell_color = self.grid_colors['obstacle'] if self.grid_obstacles[row][col] else self.grid_colors['free']
                pg.draw.rect(self.screen, cell_color, rect, 0)
                policy = self.grid_state[row][col]

                if policy != ' ':
                    self.screen.blit(self.images[policy], (x + self.cell_size / 4, y + self.cell_size / 4))
                if not(self.start_pos is None) and self.start_pos[:2]  == [row, col]:
                    pg.draw.rect(self.screen, cell_color, rect, 0)
                    self.screen.blit(self.images['start'], (x, y + self.cell_size / 4))
                    if policy != ' ':
                        self.screen.blit(self.images[policy], (x + self.cell_size / 2, y + self.cell_size / 4))
    @staticmethod
    def smooth_path(path, weight_data=0.5, weight_smooth=0.1, tolerance=0.000001):
        newpath = deepcopy(path)
        while True:
            totalChange = 0.
            for i in range(len(path)):
                if i != 0 and i != (len(path) - 1):
                    for dim in range(len(path[i])):
                        oldVal = newpath[i][dim]
                        newpath[i][dim] = newpath[i][dim] + \
                                          weight_data * (path[i][dim] - newpath[i][dim]) + \
                                          weight_smooth * (
                                                      newpath[i + 1][dim] + newpath[i - 1][dim] - 2 * newpath[i][
                                                  dim])
                        totalChange += abs(oldVal - newpath[i][dim])
            if totalChange < tolerance:
                break
        return newpath  # Leave this line for the grader!



if __name__ == "__main__":
    motiongui = PathSmoothingGUI()
    motiongui.start(fps=10)
