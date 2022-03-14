import random
import sys

import math
import pygame as pg
import matplotlib.pyplot as plt
import utils
import numpy as np

pg.font.init()
font_size = 20
font = pg.font.SysFont("monospace", font_size)
input_width = font_size*2
input_height = font_size*1.5
label_width = font_size*12
label_height = font_size*1.5

panel_width = input_width+label_width

win_width = 1500
robot_size = win_width/20

cell_width = robot_size*1.2
outline = 4

plot_height = win_width/3
plot_width = win_width
robot_x = random.randint(0, win_width-1) + panel_width

mu = robot_x
sigma_init = 200

ratio = [0.5, 1, 2, 4, 8]
motion_sigma = 10.
measurement_sigma = motion_sigma/ratio[1]

constant_shift = 0.5
step_size = 10

win_height = cell_width+plot_height


def main():
    global screen, robot_x, mu, sigma_init
    pg.init()
    screen = pg.display.set_mode((panel_width+win_width, cell_width+plot_height))
    screen.fill('black')

    parameters = ['sigma_init', 'measurement_sigma', 'motion_sigma', 'step_size']
    input_boxes = [InputBox(0, label_height*i, screen=screen, name=name) for i, name in enumerate(parameters)]
    move_text = "For motion updates use the arrow keys and use the m key for measurement updates."
    utils.blit_text(screen, move_text, (0, len(parameters)*label_height+10), width=panel_width, height=win_height, color='white', font=font)
    while True:
        drawgrid2()
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    action = -1 * step_size
                elif event.key == pg.K_RIGHT:
                    action = 1 * step_size
                else:
                    action = False
                if action:
                    mu, sigma_init = motion_update(mu, sigma_init, action)
                    true_move = np.random.normal(action, motion_sigma, 1)[0]
                    robot_x = (robot_x + true_move)
                    # bound movements to grid limits
                    robot_x = max(min(win_width-1+panel_width, robot_x), 0+panel_width)
                if event.key == pg.K_m:
                    measurement = np.random.normal(robot_x, measurement_sigma, 1)[0]
                    print(f'z = {measurement} truth = {robot_x}')
                    mu, sigma_init = measurement_update(mu, sigma_init, measurement, measurement_sigma)
            if event.type == pg.MOUSEBUTTONDOWN:
                for box in input_boxes:
                    box.handle_event(event)
            elif event.type == pg.KEYDOWN:
                for box in input_boxes:
                    if box.active:
                        box.handle_event(event)
            for box in input_boxes:
                box.draw()
        pg.display.flip()


def drawgrid2():
    robot = pg.image.load('robot2.png')
    robot = pg.transform.smoothscale(robot, (robot_size, robot_size))
    y = plot_height
    #
    # screen.fill('black')
    rect = pg.Rect(panel_width+outline, y+outline, win_width - outline, cell_width - outline)
    pg.draw.rect(screen, (200, 200, 200), rect, 0)

    screen.blit(robot, [robot_x-robot_size/2, y + cell_width/8])

    gauss = gauss2surface(mu, sigma_init)
    gauss = pg.transform.smoothscale(gauss, (plot_width-outline, plot_height-outline))
    screen.blit(gauss, [panel_width+outline, outline, win_width-outline, plot_height])
    plt.close()


def motion_update(mu, sigma, action):
    new_mu = mu + action
    new_sigma = np.sqrt(sigma**2 + motion_sigma**2)
    return new_mu, new_sigma


def measurement_update(mu, sigma, mu2, sigma2):
    new_mu = (mu*sigma2**2 + mu2*sigma**2) / (sigma**2+sigma2**2)
    new_sigma = 1/(1/(sigma**2) + 1/(sigma2**2))
    new_sigma = np.sqrt(new_sigma)
    print(f'sigma1 = {sigma} sigma2 = {sigma2} new_sigma = {new_sigma} diff = {new_sigma-sigma}')
    return new_mu, new_sigma


def gaussian(x, mu, sigma):
    return 1/(np.sqrt(2*np.pi*sigma**2))*np.exp(-0.5*(((x-mu)**2)/sigma**2))


def gauss2surface(mu, sigma):
    x = np.linspace(0, win_width, win_width)
    plt.figure(figsize=(10, 5))
    fig = plt.gcf()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    plt.xlim(0, win_width)
    plt.ylim(0, 0.1)
    plt.plot(x, gaussian(x, mu-panel_width, sigma), color='blue')

    surface = utils.fig2surface(fig)
    return surface

class InputBox:
    def __init__(self, x, y, screen, name=''):
        global sigma_init, motion_sigma, measurement_sigma, step_size
        self.rect = pg.Rect(x+label_width, y, input_width, input_height)
        self.color = (200, 200, 200)
        self.color_active = pg.Color('dodgerblue2')
        self.color_inactive = 'white'
        self.text = ''
        self.name = name
        self.font = font
        self.txt_surface = self.font.render('', 1, 'white')
        match self.name:
            case 'sigma_init':
                p = sigma_init
            case 'motion_sigma':
                p = motion_sigma
            case 'measurement_sigma':
                p = measurement_sigma
            case 'step_size':
                p = step_size
        self.txt_surface = self.font.render(str(round(p, 2)), 1, self.color_inactive)

        self.active = False
        self.screen = screen

        label_box1 = pg.Rect(x+2, y, label_width, label_height)
        label = self.font.render(f"{name}:          ", 1, 'white')
        self.screen.blit(label, label_box1)

    def handle_event(self, event):
        global sigma_init, motion_sigma, measurement_sigma, step_size
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    match self.name:
                        case 'sigma_init':
                            sigma_init = float(self.text)
                        case 'motion_sigma':
                            motion_sigma = float(self.text)
                        case 'measurement_sigma':
                            measurement_sigma = float(self.text)
                        case 'step_size':
                            step_size = float(self.text)
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, 'white')

    def draw(self):
        # delete old render before rerendering to avoid text overlap
        pg.draw.rect(self.screen, 'black', self.rect, 0)
        # Blit the text.
        self.screen.blit(self.txt_surface, (self.rect.x+2, self.rect.y))
        # Blit the rect.
        pg.draw.rect(self.screen, self.color, self.rect, 1)
# print(measurement_update(10, 2, 12, 2))
main()