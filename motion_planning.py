import pygame as pg
from datatypes import RobotGUI


class MotionPlanningGUI(RobotGUI):
    def __init__(self, robot='robot1', world_size=(10, 10)):
        scale = int((1/world_size[0])*700)
        self.window_width = scale * world_size[0]
        self.window_height = scale * world_size[1]
        super().__init__(robot_img=robot, screen_width=self.window_width, height_width_ratio=self.window_height/self.window_width)
        self.grid = [[0 for row in range(self.world_size[0])] for col in range(self.world_size[1])]
        self.cell_size = scale
        self.outline_thickness = 2

    def draw(self):
        for i, y in enumerate(range(0, self.window_height, self.cell_size)):
            for j, x in enumerate(range(self.window_width, self.cell_size)):
                rect = pg.Rect(x + self.outline_thickness, y + self.outline_thickness, self.cell_size - self.outline_thickness,
                               self.cell_size - self.outline_thickness)
                cell_color = 'white' if self.grid[i][j] else 'gray'
                pg.draw.rect(self.screen, cell_color, rect, 0)
                if j == self.robot.x and i == self.robot.y:
                    self.screen.blit(self.robot.image, [x + self.cell_size/4, y + self.cell_size / 4])

if __name__ == "__main__":
    motiongui = MotionPlanningGUI()
    motiongui.start()