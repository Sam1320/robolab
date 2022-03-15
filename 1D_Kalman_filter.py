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
sigma = 200

ratio = [0.5, 1, 2, 4, 8]
motion_sigma = 10.
measurement_sigma = motion_sigma/ratio[1]

constant_shift = 0.5
step_size = 10

win_height = cell_width+plot_height
plot_color = 'blue'

params = {'mu': robot_x, 'sigma': sigma, 'measurement_sigma': measurement_sigma, 'motion_sigma': motion_sigma,
          'step_size': step_size}
def main():
    global screen, robot_x, plot_color, params
    pg.init()
    screen = pg.display.set_mode((panel_width+win_width, cell_width+plot_height))
    screen.fill('black')

    input_boxes = {name:InputBox(0, label_height*i, screen=screen, name=name, value=params[name], font=font)
                   for i, name in enumerate(params)}
    move_text = "For motion updates use the arrow keys and use the m key for measurement updates."
    utils.blit_text(screen, move_text, (0, len(params)*label_height+10), width=panel_width, height=win_height, color='white', font=font)
    while True:
        drawgrid()
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    action = -1 * params['step_size']
                elif event.key == pg.K_RIGHT:
                    action = 1 * params['step_size']
                else:
                    action = False
                if action:
                    params['mu'], params['sigma'] = motion_update(params['mu'], params['sigma'], action, params['motion_sigma'])
                    true_move = np.random.normal(action, params['motion_sigma'], 1)[0]
                    robot_x = (robot_x + true_move)
                    # bound movements to grid limits
                    plot_color = 'red'
                    robot_x = max(min(win_width-1+panel_width, robot_x), 0+panel_width)
                if event.key == pg.K_m:
                    measurement = np.random.normal(robot_x, params['measurement_sigma'], 1)[0]
                    print(f'z = {measurement} truth = {robot_x}')
                    params['mu'], params['sigma'] = measurement_update(params['mu'], params['sigma'], measurement, params['measurement_sigma'])
                    plot_color = 'blue'
                print(f'mu = {params["mu"]} truth = {robot_x}')

            if event.type == pg.MOUSEBUTTONDOWN:
                for box in input_boxes.values():
                    box.handle_event(event)

            elif event.type == pg.KEYDOWN:
                for box in input_boxes.values():
                    if box.active:
                        params[box.name] = box.handle_event(event)
            for box in input_boxes.values():
                box.draw()
        pg.display.flip()


def drawgrid():
    # screen.fill('black')
    robot = pg.image.load('robot2.png')
    robot = pg.transform.smoothscale(robot, (robot_size, robot_size))
    y = plot_height
    #
    # screen.fill('black')
    rect = pg.Rect(panel_width+outline, y+outline, win_width - outline, cell_width - outline)
    pg.draw.rect(screen, (200, 200, 200), rect, 0)

    screen.blit(robot, [robot_x-robot_size/2, y + cell_width/8])

    gauss = gauss2surface(params['mu'], params['sigma'])
    gauss = pg.transform.smoothscale(gauss, (plot_width-outline, plot_height-outline))
    screen.blit(gauss, [panel_width+outline, outline, win_width-outline, plot_height])
    plt.close()


def motion_update(mu, sigma, motion, motion_sigma):
    new_mu = mu + motion
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
    plt.plot(x, gaussian(x, mu-panel_width, sigma), color=plot_color)

    surface = utils.fig2surface(fig)
    return surface


class InputBox:
    #todo: fix numbers displayed outside of input box
    def __init__(self, x, y, screen, name, value, font):
        self.rect = pg.Rect(x+label_width, y, input_width+10, input_height)
        self.color = (200, 200, 200)
        self.color_active = pg.Color('dodgerblue2')
        self.color_inactive = 'white'
        self.text = ''
        self.name = name
        self.value = value
        self.font = font
        self.txt_surface = self.font.render('', 1, 'white')
        self.txt_surface = self.font.render(str(round(self.value, 2)), 1, self.color_inactive)

        self.active = False
        self.screen = screen

        label_box1 = pg.Rect(x+2, y, label_width, label_height)
        label = self.font.render(f"{self.name}:          ", 1, 'white')
        self.screen.blit(label, label_box1)

    def handle_event(self, event):
        # global sigma, motion_sigma, measurement_sigma, step_size
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
                    self.value = float(self.text)
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, 'white')
        return self.value

    def draw(self):
        # delete old render before rerendering to avoid text overlap
        pg.draw.rect(self.screen, 'black', self.rect, 0)
        # Blit the text.
        self.screen.blit(self.txt_surface, (self.rect.x+2, self.rect.y))
        # Blit the rect.
        pg.draw.rect(self.screen, self.color, self.rect, 1)


main()