from src.datatypes import GridGUI
from src import utils
import pygame as pg


class OptimumPolicyGUI(GridGUI):
    def __init__(self, world_size=(10, 6), load_grid=False, obstacle_prob=0.2, costs=(1, 1, 1), init_orientation=0,
                 robot_img='car.png', path_arrows=True):
        super().__init__(world_size=world_size, load_grid=load_grid, obstacle_prob=obstacle_prob,
                         robot_img=robot_img, path_arrows=path_arrows)
        self.costs = costs
        self.init_orientation = init_orientation
        match init_orientation:
            case 0:
                self.image_rotation = 0
            case 1:
                self.image_rotation = 90
            case 2:
                self.image_rotation = 180
            case 3:
                self.image_rotation = -90

    def handle_left_click(self):
        pos = pg.mouse.get_pos()
        pos = list(self.coords_to_row_col(pos[0], pos[1]))
        if not self.grid_obstacles[pos[0]][pos[1]]:
            if self.start_pos:
                self.grid_state[self.start_pos[0]][self.start_pos[1]] = ' '
            self.start_pos = [pos[0], pos[1], self.init_orientation]
            self.grid_state[pos[0]][pos[1]] = 'S'

    def update_grid_state(self):
        if self.start_pos and self.goal:
            #TODO: KeyError: 'None' when no path is found
            self.grid_state = utils.optimum_policy2D(self.grid_obstacles, self.start_pos, self.goal, cost=self.costs)


if __name__ == "__main__":
    gui = OptimumPolicyGUI()
    gui.start(verbose=False)