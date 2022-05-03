import sys
import pygame as pg
from datatypes import RobotGUI
import math

ANGULAR_STEP = 0.1
LINEAR_STEP = 0.2


class ParticleFilterGUI(RobotGUI):
    def __init__(self):
        super().__init__()
        self.moving = False

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                angular, linear = 0, 0
                if event.key == pg.K_LEFT:
                    angular = 1 * ANGULAR_STEP
                elif event.key == pg.K_RIGHT:
                    angular = -1 * ANGULAR_STEP
                elif event.key == pg.K_UP:
                    linear = 1 * LINEAR_STEP
                elif event.key == pg.K_DOWN:
                    linear = -1 * LINEAR_STEP
                self.linear = linear
                self.angular = angular
                self.moving = True
            elif event.type == pg.KEYUP:
                self.moving = False

        if self.moving:
            self.robot.move(self.linear, self.angular)


class Person:
    def __init__(self, name, ln):
        self.name = name
        self.ln = ln
        self.fn = name + ln


particleGUI = ParticleFilterGUI()
particleGUI.start()