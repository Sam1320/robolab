import pygame as pg
from src.datatypes import GridGUI
from src import utils


class AStartGUI(GridGUI):
    def __int__(self, world_size=(10, 6), load_grid=False, obstacle_prob=0.2, path_arrows=False):
        super().__init__(world_size=world_size, load_grid=load_grid, obstacle_prob=obstacle_prob, path_arrows=path_arrows)

    def handle_left_click(self):
        pos = pg.mouse.get_pos()
        pos = list(self.coords_to_row_col(pos[0], pos[1]))
        # only execute command if cell is free
        if not self.grid_obstacles[pos[0]][pos[1]]:
            # clear the previous cell
            if self.start_pos:
                self.grid_state[self.start_pos[0]][self.start_pos[1]] = ' '
            self.grid_state[pos[0]][pos[1]] = 'S'
            self.start_pos = pos


    def update_grid_state(self):
        if self.start_pos and self.goal:
            self.grid_state, self.resign = utils.a_star_search(self.grid_obstacles, self.start_pos, self.goal, utils.heuristic)


if __name__ == "__main__":
    motiongui = AStartGUI()
    motiongui.start(fps=10)

