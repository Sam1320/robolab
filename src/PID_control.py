import math
import os.path

import pygame as pg
import env
from src.datatypes import RobotGUI, RobotCar


class PIDControlGUI(RobotGUI):
    """
    This class is used to control a robot using a PID controller.
    """
    def __init__(self, robot_img='car.png', screen_width=1000, height_width_ratio=1/2, robot_size='medium'):
        super().__init__(robot_img=robot_img, screen_width=screen_width,
                         height_width_ratio=height_width_ratio, robot_size=robot_size)
        self.scroll_speed = 1
        self.dt = 1
        self.scroll = 0
        self.background_image_path = os.path.join(env.images_path, 'road_big.png')

        self.proportional_gain = 0.2
        self.integral_gain = 0.1
        self.derivative_gain = 0.1

    def init_pygame(self):
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        self.car_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, self.robot_img)).convert_alpha(),
                                                  (self.robot_size, self.robot_size))
        # rotate the car image to look east instead of north
        self.car_img = pg.transform.rotate(self.car_img, -90)
        self.robot = RobotCar(image=self.car_img)
        self.robot.set(500, 5, 0)
        self.bg_image = pg.image.load(self.background_image_path).convert()
        # resize the background image to fit the screen
        self.bg_image = pg.transform.smoothscale(self.bg_image, (self.screen_width, self.screen_height))
        self.bg_image_width = self.bg_image.get_rect().width
        self.n_tiles = math.ceil(self.screen_width/self.bg_image_width) + 2

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 1
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return 1
                elif event.key == pg.K_RIGHT:
                    self.scroll_speed += 1
                elif event.key == pg.K_LEFT:
                    # truncate minimum scroll speed to 0
                    self.scroll_speed = max(0, self.scroll_speed - 1)

        # Draw one background image per tile and scroll it
        for i in range(self.n_tiles):
            self.screen.blit(self.bg_image, (i*self.bg_image_width - self.scroll, 0))
        self.scroll += self.scroll_speed
        if self.scroll > self.bg_image_width:
            self.scroll = 0
            print('reset scroll')

        cte = self.robot.y
        steer = - self.proportional_gain * cte
        self.robot.move(steer, self.dt)

        # convert robot coords to screen coords and draw the robot on the screen
        robot_x, robot_y = self.world2screen((self.robot.x, self.robot.y))
        #compensate x coordinate for scrolling
        robot_x = 500
        # center of the robot should coincide with center of the image instead of the upper left corner
        frame = self.robot.image.get_rect()
        frame.center = (robot_x, robot_y)
        self.screen.blit(self.robot.image, frame)


    def world2screen(self, pos):
        """Translate y coordinate from the origin to the center of the screen"""
        x, y = pos
        return x, self.screen_height/2 - y





if __name__ == """__main__""":
    gui = PIDControlGUI()
    gui.start(verbose=False)