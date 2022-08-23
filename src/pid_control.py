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
                 x_init=0.0, y_init=0.7, drift=10, proportional_gain=.1, differential_gain=3.0, integral_gain=0.001):
        super().__init__(robot_img=robot_img, screen_width=screen_width,
                         height_width_ratio=height_width_ratio, robot_size=robot_size)
        self.robot_speed = 4
        self.dt = 1
        self.scroll = 0
        self.background_image_path = os.path.join(env.images_path, 'road.png')
        self.drift = drift

        self.proportional_gain = proportional_gain # 0.023
        self.integral_gain = integral_gain # 2.34e-06
        self.differential_gain = differential_gain #0.464

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


        # load and transform clock image and store in variable
        self.clock_img = pg.image.load(os.path.join(env.images_path, 'sand-clock.png')).convert_alpha()
        # resize the clock image to twice the size of the car
        self.clock_img = pg.transform.smoothscale(self.clock_img, (self.robot_size*2, self.robot_size*2))
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
                elif event.key == pg.K_UP:
                    self.drift += 1
                    self.robot.set_steering_drift(math.radians(self.drift))
                elif event.key == pg.K_DOWN:
                    # self.drift = max(0, self.drift - 1)
                    self.drift -= 1
                    self.robot.set_steering_drift(math.radians(self.drift))
                elif event.key == pg.K_t:
                    current_y_pos = self.robot.y
                    current_x_pos = self.robot.x
                    # plot clock and loading message
                    message = 'Finding best PID parameters given the current car position, speed and drift...'
                    self.screen.blit(self.clock_img, (self.screen_width/2 - self.clock_img.get_rect().width/2,
                                                        self.screen_height/2 - self.clock_img.get_rect().height/2))
                    self.screen.blit(self.font.render(message, True, (255, 255, 255)),
                                     (self.screen_width/2 - self.font.size(message)[0]/2,
                                    self.screen_height/2 + self.clock_img.get_rect().height/2 + 10))
                    pg.display.flip()
                    params, best_error = self.twiddle(x=current_x_pos, y=current_y_pos, speed=self.robot_speed)
                    # reset parameters and robot position
                    self.proportional_gain = params[0]
                    self.differential_gain = params[1]
                    self.integral_gain = params[2]
                    self.robot = RobotCar(image=self.car_img, length=self.car_length)
                    self.robot.set(current_x_pos, current_y_pos, 0)
                    self.robot.set_steering_drift(math.radians(self.drift))
                    self.prev_x_pos = self.robot.x
                    self.prev_cte = self.robot.y
                    self.int_cte = 0

        # calculate scroll amount from the change in x position of the robot
        self.scroll += self.robot.x - self.prev_x_pos
        self.prev_x_pos = self.robot.x

        # Draw one background image per tile and scroll it
        for i in range(self.n_tiles):
            self.screen.blit(self.bg_image, (i*self.bg_image_width - self.scroll, 0))
        if self.scroll > self.bg_image_width:
            self.scroll = 0

        cte = self.robot.y
        diff_cte = (self.robot.y - self.prev_cte) / self.dt
        self.prev_cte = cte
        self.int_cte += cte * self.dt
        steer = self.calculate_steering_command(cte, diff_cte, self.int_cte, self.proportional_gain,
                                                self.integral_gain, self.differential_gain)
        self.robot.move(steer, self.robot_speed)

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
        self.draw_label('I: ' + str(round(self.integral_gain, 8)), x=10, y=50)
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

    def make_robot(self, image=None, x=0, y=0, angle=0):
        """ Creates robot object and sets initial position """
        robot = RobotCar(length=self.car_length) if image is None else RobotCar(image=image, length=self.car_length)
        robot.set(x, y, angle)
        robot.set_steering_drift(math.radians(self.drift))
        return robot

    def run(self, robot, params, n=200, speed=1.0):
        """Simulate 2n time-steps of the robot moving at a constant speed.
        Return the average squared cte over the last n time-steps."""
        err = 0
        prev_cte = robot.y
        prev_x_pos = robot.x
        int_cte = 0
        for i in range(2 * n):
            cte = robot.y
            delta_x = robot.x - prev_x_pos
            if delta_x < 0:
                cte += delta_x*0.001
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

    def twiddle(self, x, y, tolerance=0.0001, angle=0, n=200, speed=1.0):
        """
        This function is used to tune the PID controller parameters.
        It takes the current state of the robot and calculates the best parameters.
        Tolerance is the sum of the probing values. (as twiddle converges the sum gets smaller)
        """
        # initial proportional, derivative, integral gains
        p = [0.0, 0.0, 0.0]
        # initial probing values
        dp = [.5, 1, .5]
        robot = self.make_robot(x=x, y=y, angle=angle)
        best_err = self.run(robot, p, speed=speed)
        it = 0
        while sum(dp) > tolerance:
            print("Iteration {}, best error = {}".format(it, best_err))
            for i in range(len(p)):
                p[i] += dp[i]
                robot = self.make_robot(x=x, y=y, angle=angle)
                err = self.run(robot, p, speed=speed)
                # print parameters and error
                print('P: ', p, 'err: ', err)
                if err < best_err:
                    best_err = err
                    dp[i] *= 1.1
                else:
                    p[i] -= 2 * dp[i]
                    robot = self.make_robot(x=x, y=y, angle=angle)
                    err = self.run(robot, p, speed=speed)
                    # print parameters and error
                    print('P: ', p, 'err: ', err)
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