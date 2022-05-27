from src.datatypes import GridGUI
from src import utils


class DynamicProgrammingGUI(GridGUI):
    def __init__(self, world_size=(10, 6), load_grid=False, obstacle_prob=0.2, path_arrows=True):
        super().__init__(world_size=world_size, load_grid=load_grid, obstacle_prob=obstacle_prob, path_arrows=path_arrows)

    def update_grid_state(self):
        if self.goal:
            self.grid_state = utils.dynamic_programming_search(self.grid_obstacles, self.goal, cost=1)


if __name__ == "__main__":
    gui = DynamicProgrammingGUI()
    gui.start(verbose=False)