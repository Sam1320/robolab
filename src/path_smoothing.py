import pygame as pg
from src.datatypes import GridGUI
from src import utils
from copy import deepcopy


class PathSmoothingGUI(GridGUI):
    def __init__(self, world_size=(5, 5), load_grid=False, obstacle_prob=0.2, draw_smooth_points=False):
        super().__init__(world_size=world_size, load_grid=load_grid, obstacle_prob=obstacle_prob)
        self.path_coords = []
        self.smoothed_path_coords = []
        self.data_weigth = 0.5
        self.smooth_weight = 0.5
        self.draw_smooth_points = draw_smooth_points
        # extend the length of the path by n between each point depending on the number of cells (smoother lines)
        if 2 < world_size[0] * world_size[1] < 20:
            self.extend_path_n = 8
        elif 20 <= world_size[0] * world_size[1] < 40:
            self.extend_path_n = 4
        else:
            self.extend_path_n = 2

    def handle_left_click(self):
        pos = pg.mouse.get_pos()
        if self.start_pos:
            self.grid_state[self.start_pos[0]][self.start_pos[1]] = ' '
        self.start_pos = list(self.coords_to_row_col(pos[0], pos[1]))
        self.grid_state[self.start_pos[0]][self.start_pos[1]] = 'S'

    def handle_mouse_wheel(self, event, delta=0.01):
        self.smooth_weight += event.y * (self.smooth_weight + delta) * 0.1
        self.data_weigth -= event.y * (self.data_weigth + delta) * 0.1

        # truncate weights to be between 0 and 0.5
        self.smooth_weight = max(0, self.smooth_weight)
        self.smooth_weight = min(0.5, self.smooth_weight)
        self.data_weigth = max(0, self.data_weigth)
        self.data_weigth = min(0.5, self.data_weigth)

    def update_grid_state(self):
        if self.start_pos and self.goal:
            self.grid_state, self.path_coords = utils.a_star_search(self.grid_obstacles, self.start_pos, self.goal,
                                                                    utils.heuristic, return_path_coords=True)
            # extend the length of the path by n between each point before smoothing
            path_coords_extended = utils.extend_path_length(self.path_coords, n=self.extend_path_n)
            self.smoothed_path_coords = utils.smooth_path(path_coords_extended, weight_smooth=self.smooth_weight,
                                                          weight_data=self.data_weigth)
    def draw(self):
        self.screen.fill((0, 0, 0))
        to_blit = []
        for row, y in enumerate(range(0, self.window_height, self.cell_size)):
            for col, x in enumerate(range(0, self.window_width, self.cell_size)):
                rect = pg.Rect(x + self.outline_thickness, y + self.outline_thickness, self.cell_size - self.outline_thickness,
                               self.cell_size - self.outline_thickness)
                cell_color = self.grid_colors['obstacle'] if self.grid_obstacles[row][col] else self.grid_colors['free']
                pg.draw.rect(self.screen, cell_color, rect, 0)
                policy = self.grid_state[row][col]
                if policy in ('*', 'S', '!'):
                    # store coordinates and policy in to_blit to draw later
                    to_blit.append(((x, y), policy))

        path_coords_screen = self.convert_points_to_screen_coords(self.path_coords)
        smoothed_path_coords_screen = self.convert_points_to_screen_coords(self.smoothed_path_coords)

        # draw path coordinate points
        for point in path_coords_screen:
            pg.draw.circle(self.screen, self.grid_colors['path'], point, self.cell_size / 10)
        if self.draw_smooth_points:
            # draw smoothed path coordinate points
            for point in smoothed_path_coords_screen:
                pg.draw.circle(self.screen, self.grid_colors['smooth_path'], point, self.cell_size / 10)

        if self.path_coords:
            # draw lines from path points
            self.draw_lines_from_points(self.path_coords, self.grid_colors['path'], width=2)
            # draw lines from smoothed path points
            self.draw_lines_from_points(self.smoothed_path_coords, self.grid_colors['smooth_path'], width=2)

        # draw images stored in to_blit on top of the path lines
        for point, policy in to_blit:
            self.screen.blit(self.images[policy], (point[0] +self.cell_size/4, point[1]+ self.cell_size/4))

    def convert_points_to_screen_coords(self, points):
        points_screen_coords = []
        for point in points:
            point_screen_coords = self.row_col_to_screen_coords(point[0], point[1])
            point_screen_coords = (point_screen_coords[0] + self.cell_size / 2, point_screen_coords[1] + self.cell_size / 2)
            points_screen_coords.append(point_screen_coords)
        return points_screen_coords

    def draw_lines_from_points(self, points, color, width=1):
        # convert points to screen coords
        points_screen_coords = []
        for point in points:
            point_screen_coords = self.row_col_to_screen_coords(point[0], point[1])
            point_screen_coords = (point_screen_coords[0] + self.cell_size / 2, point_screen_coords[1] + self.cell_size / 2)
            points_screen_coords.append(point_screen_coords)
        # draw lines
        pg.draw.lines(self.screen, color, False, points_screen_coords, width=width)

    def row_col_to_screen_coords(self, row, col):
        return (col * self.cell_size + self.outline_thickness, row * self.cell_size + self.outline_thickness)




if __name__ == "__main__":
    motiongui = PathSmoothingGUI()
    motiongui.start(fps=10, verbose=False)
