import math
import os.path

import pygame as pg
import env
from src.datatypes import RobotGUI, RobotCar


class PIDControlGUI(RobotGUI):
    """
    This class is used to control a robot using a PID controller.
    """
    def __init__(self, robot_img='car.png', screen_width=1500, height_width_ratio=1/2, robot_size='medium',
                 x_init=0.0, y_init=0.5, drift=10, proportional_gain=.1, differential_gain=3.0, integral_gain=0.001):
        super().__init__(robot_img=robot_img, screen_width=screen_width,
                         height_width_ratio=height_width_ratio, robot_size=robot_size)
        self.robot_speed = 5
        self.dt = 1
        self.scroll = 0
        self.background_image_path = os.path.join(env.images_path, 'road.png')
        self.drift = drift

        self.proportional_gain = proportional_gain
        self.integral_gain = integral_gain
        self.differential_gain = differential_gain

        self.x_init = (x_init*(self.screen_width/2)) + self.screen_width/2  # x position is fixed
        self.y_init = (y_init*(self.screen_height/2))

    def init_pygame(self):
        pg.init()
        self.font = pg.font.SysFont('Arial', 20)
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        self.car_img = pg.transform.smoothscale(pg.image.load(os.path.join(env.images_path, self.robot_img)).convert_alpha(),
                                                  (self.robot_size, self.robot_size))
        # rotate the car image to look east instead of north
        self.car_img = pg.transform.rotate(self.car_img, -90)
        self.car_length = self.car_img.get_rect().width*0.8
        self.robot = RobotCar(image=self.car_img, length=self.car_length)
        self.robot.set(self.x_init, self.y_init, 0)
        # sets steering drift from degrees to radians
        self.robot.set_steering_drift(math.radians(self.drift))
        # initial cross track error and integral cross track error
        self.prev_x_pos = self.robot.x
        self.prev_cte = self.robot.y
        self.int_cte = 0
        self.bg_image = pg.image.load(self.background_image_path).convert()
        # resize the background image to fit the screen
        self.bg_image = pg.transform.smoothscale(self.bg_image, (self.screen_width, self.screen_height))
        self.bg_image_width = self.bg_image.get_rect().width
        self.n_tiles = math.ceil(self.screen_width/self.bg_image_width) + 2

        # robot_copy = self.make_robot()
        # self.run(robot_copy, [self.proportional_gain, self.derivative_gain, self.integral_gain], n=200, speed=self.robot_speed)
        #
        # params, best_error = self.twiddle()
        # # print parameters and best error
        # print('PID parameters: ', params)
        # print('Best error: ', best_error)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 1
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return 1
                elif event.key == pg.K_RIGHT:
                    self.robot_speed += 1
                elif event.key == pg.K_LEFT:
                    # truncate minimum scroll speed to 0
                    self.robot_speed = max(0, self.robot_speed - 1)
                elif event.key == pg.K_t:
                    params, _ = self.twiddle()
                    self.proportional_gain = params[0]
                    self.differential_gain = params[1]
                    self.integral_gain = params[2]
                    self.robot = self.make_robot(image=self.car_img)

        # calculate scroll amount from the change in x position of the robot
        self.scroll += self.robot.x - self.prev_x_pos
        self.prev_x_pos = self.robot.x

        # Draw one background image per tile and scroll it
        for i in range(self.n_tiles):
            self.screen.blit(self.bg_image, (i*self.bg_image_width - self.scroll, 0))
        if self.scroll > self.bg_image_width:
            self.scroll = 0
            print('reset scroll')

        cte = self.robot.y
        diff_cte = (self.robot.y - self.prev_cte) / self.dt
        self.prev_cte = cte
        self.int_cte += cte * self.dt
        steer = self.calculate_steering_command(cte, diff_cte, self.int_cte, self.proportional_gain,
                                                self.integral_gain, self.differential_gain)
        self.robot.move(steer, self.robot_speed)
        # print(cte)
        # convert robot coords to screen coords and draw the robot on the screen
        robot_x, robot_y = self.world2screen((self.robot.x, self.robot.y))
        # fix robot screen position to initial position
        robot_x = self.x_init

        # center of the robot should coincide with center of the image instead of the upper left corner
        frame = self.robot.image.get_rect()
        frame.center = (robot_x, robot_y)
        self.screen.blit(self.robot.image, frame)

        # draw label on upper left corner to show current cte
        self.draw_label('CTE: ' + str(round(cte, 2)), x=10, y=10)
        # draw labels to show PID parameters
        self.draw_label('P: ' + str(round(self.proportional_gain, 4)), x=10, y=30)
        self.draw_label('I: ' + str(round(self.integral_gain, 4)), x=10, y=50)
        self.draw_label('D: ' + str(round(self.differential_gain, 4)), x=10, y=70)
        # draw label to show drift
        self.draw_label('Drift: ' + str(round(math.degrees(self.robot.steering_drift), 2)), x=10, y=90)
        # draw label to show speed
        self.draw_label('Speed: ' + str(self.robot_speed), x=10, y=110)


    def draw_label(self, text, x, y):
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)


    def make_robot(self, image=None):
        """ Creates robot object and sets initial position """
        robot = RobotCar(length=self.car_length) if image is None else RobotCar(image=image, length=self.car_length)
        robot.set(self.x_init, self.y_init, 0)
        robot.set_steering_drift(math.radians(self.drift))
        return robot

    def run(self, robot, params, n=100, speed=1.0):
        """Simulate 2n time-steps of the robot moving at a constant speed.
        Return the average squared cte over the last n time-steps."""
        err = 0
        prev_cte = robot.y
        int_cte = 0
        for i in range(2 * n):
            cte = robot.y
            diff_cte = cte - prev_cte
            int_cte += cte
            prev_cte = cte
            steer = -params[0] * cte - params[1] * diff_cte - params[2] * int_cte
            robot.move(steer, speed)
            if i >= n:
                err += cte ** 2
        average_error = err / n
        print('average error: ', average_error)
        return average_error

    def twiddle(self, tolerance=0.1):
        """
        This function is used to tune the PID controller parameters.
        """
        # initial proportional, derivative, integral gains
        p = [0.0, 0.0, 0.0]
        # initial probing values
        dp = [1.0, 1.0, 1.0]
        robot = self.make_robot()
        best_err = self.run(robot, p, speed=self.robot_speed)
        it = 0
        while sum(dp) > tolerance:
            print("Iteration {}, best error = {}".format(it, best_err))
            for i in range(len(p)):
                p[i] += dp[i]
                robot = self.make_robot()
                err = self.run(robot, p, speed=self.robot_speed)

                if err < best_err:
                    best_err = err
                    dp[i] *= 1.1
                else:
                    p[i] -= 2 * dp[i]
                    robot = self.make_robot()
                    err = self.run(robot, p, speed=self.robot_speed)

                    if err < best_err:
                        best_err = err
                        dp[i] *= 1.1
                    else:
                        p[i] += dp[i]
                        dp[i] *= 0.9
            it += 1
        return p, best_err

    def calculate_steering_command(self, cte, diff_cte, int_cte, proportional_gain, integral_gain, differential_gain):
        """uses the PID controller to calculate the steering command"""
        steer = - proportional_gain * cte - integral_gain * int_cte - differential_gain * diff_cte
        return steer


    def world2screen(self, pos):
        """Translate x and y coordiates to the center of the screen"""
        x, y = pos
        return x + self.screen_width/2, self.screen_height/2 - y





if __name__ == """__main__""":
    gui = PIDControlGUI()
    gui.start(verbose=False)