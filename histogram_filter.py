import pygame as pg
import sys
import random
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

black = (0, 0, 0)
white = (200, 200, 200)
red = (255, 150, 70)
green = (128, 255, 128)
grid_width = 4
grid_height = 1
#todo adapt scale to actual screensize
scale = int((1/grid_width)*600)
font_size = int(scale/10)
win_height = grid_height*scale
win_width = grid_width*scale
grid = [[random.sample(['green', 'red'], 1)[0] for _ in range(grid_width)] for _ in range(grid_height)]
# grid = ['green', 'red', 'red', 'green', 'green']
grid_colors = {'green': green, 'red': red, 'white': white, 'black': black}
cell_height = int(win_height/grid_height)
cell_width = int(win_width/grid_width)
robot_size = int(cell_height*0.5)

robot_row = 0 #random.randint(0, grid_height)
robot_col = 0 #random.randint(0, grid_width)
outline_thickness = 4
n_blocks = grid_width*grid_height
probs = [[1/n_blocks for _ in range(grid_width)] for _ in range(grid_height)]
# probs = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
# probs[0][0] = 1.
pHit = .9
pMiss = 0.1
pGood = .8
pOvershoot = 0.1
pUndershoot = 0.1
panel_height = 40

measurement_probs = {'red|red': pHit, 'green|red':pMiss, 'green|green':pHit, 'red|green':pMiss}
Z = ['red', 'red']

def main():
    global SCREEN, CLOCK, robot_row, robot_col, probs
    pg.init()
    SCREEN = pg.display.set_mode((win_width*2, win_height+panel_height))
    CLOCK = pg.time.Clock()
    SCREEN.fill(black)
    # used by InputBox

    input_box1 = InputBox(45, win_height, 50, 15, screen=SCREEN, text='pHit')
    input_boxes = [input_box1]
    while True:
        drawgrid()
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    robot_col = (robot_col - 1) % grid_width
                    action = (-1, 0)
                elif event.key == pg.K_RIGHT:
                    robot_col = (robot_col + 1) % grid_width
                    action = (1, 0)
                elif event.key == pg.K_DOWN:
                    robot_row = (robot_row + 1) % grid_height
                    action = (0, 1)
                elif event.key == pg.K_UP:
                    robot_row = (robot_row - 1) % grid_height
                    action = (0, -1)
                else:
                    action = False
                if action:
                    # apply motion
                    probs = motion_update(probs, action)
                    # sample measurement according to pHit and pMiss
                    good_measurement = random.random() < pHit
                    measurement = grid[robot_row][robot_col] if good_measurement else ('green' if grid[0][robot_col] == 'red' else 'red')
                    print(f"measurement = {good_measurement}")
                    # update probabilities given the color sensed
                    probs = measurement_update(probs, measurement)
            if event.type == pg.MOUSEBUTTONDOWN:
                for box in input_boxes:
                    box.handle_event(event)
            elif event.type == pg.KEYDOWN:
                for box in input_boxes:
                    if box.active:
                        box.handle_event(event)
                        print('wii')

            for box in input_boxes:
                box.draw()

        # display.flip() will update only a portion of the
        # screen to updated, not full area
        pg.display.flip()


def drawgrid():
    global probs
    robot = pg.image.load('robotic.png')
    robot = pg.transform.smoothscale(robot, (robot_size, robot_size))
    myfont = pg.font.SysFont("monospace", font_size)

    for i, y in enumerate(range(0, win_height, cell_height)):
        for j, x in enumerate(range(0, win_width, cell_width)):
            rect = pg.Rect(x+outline_thickness, y+outline_thickness, cell_width-outline_thickness, cell_height-outline_thickness)
            pg.draw.rect(SCREEN, grid_colors[grid[i][j]], rect, 0)
            label = myfont.render(f"p: {probs[i][j]}", 1, (0, 0, 0))
            SCREEN.blit(label, [x+(cell_width/4), y+int((3.5*cell_height/4))])
            if j == robot_col and i == robot_row:
                SCREEN.blit(robot,  [x+cell_width/4, y+cell_height/4])

    histogram = probs2surface(probs)
    histogram = pg.transform.smoothscale(histogram, (win_width, win_height))
    SCREEN.blit(histogram, [win_width, 0])


def measurement_update(p, measurement):
    new_p = [[0 for _ in range(len(p[0]))] for _ in range(len(p))]
    for i in range(len(p)):
        for j in range(len(p[0])):
            hit = measurement == grid[i][j]
            new_p[i][j] = p[i][j]*(hit*pHit + (1-hit)*pMiss)
    # normalize
    total_sum = sum([sum(row) for row in new_p]) + 1e-10
    new_p = [[round(p/total_sum, 4) for p in row] for row in new_p]
    return new_p


def motion_update(p, action):
    new_p = [[0 for _ in range(len(p[0]))] for _ in range(len(p))]
    for i in range(len(p)):
        for j in range(len(p[0])):
            # apply law of total probability. i.e. sum over all possible transitions
            t1 = pGood*p[(i-action[1])%grid_height][(j-action[0])%grid_width]                 # the robot moved correctly
            t2 = pOvershoot * p[(i-action[1]-1)%grid_height][(j-action[0]-1)%grid_width]    # the robot moved one cell too much
            t3 = pUndershoot * p[i][j]                         # the robot did not move
            new_p[i][j] = round(t1 + t2 + t3, 4)
    return new_p

# libraries



def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img


def pilImageToSurface(pilImage):
    return pg.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode).convert()


def fig2surface(fig):
    img = fig2img(fig)
    surface = pilImageToSurface(img)
    return surface


def probs2surface(probs):
    #todo: move x, y, nx, ny, xv and xy to global scope instead of calculating them every time.
    nx, ny = (len(probs[0]), len(probs))
    x = np.arange(1, nx + 1)
    y = np.arange(ny, 0, -1)
    xv, yv = np.meshgrid(x, y)
    xv = xv.flatten()
    yv = yv.flatten()
    w = [probs[i][j] for i in range(len(probs)) for j in range(len(probs[0]))]
    plt.xticks(x)
    plt.yticks(y)
    plt.hist2d(xv, yv, weights=w, bins=(nx, ny), cmap=plt.cm.jet)

    fig = plt.gcf()
    # only plot the content of the histogram (no padding or axes)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    surface = fig2surface(fig)
    return surface

class InputBox:
    def __init__(self, x, y, w, h, screen, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = (200, 200, 200)
        self.color_active = pg.Color('dodgerblue2')
        self.color_inactive = grid_colors['white']
        self.text = ''
        self.font = pg.font.SysFont("monospace", font_size)
        self.txt_surface = self.font.render('', 1, (0, 0, 0))
        self.active = False
        self.screen = screen

        label_box1 = pg.Rect(0, win_height, 100, 40)
        label = self.font.render(f"{text}:", 1, grid_colors['white'])
        self.screen.blit(label, label_box1)

    def handle_event(self, event):
        global pHit
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
                    pHit = float(self.text)
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

                # delete old render before rerendering to avoid text overlap
                pg.draw.rect(self.screen, grid_colors['black'], self.rect, 0)
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, grid_colors['white'])

    # def update(self):
    #     # Resize the box if the text is too long.
    #     width = max(200, self.txt_surface.get_width()+10)
    #     self.rect.w = width

    def draw(self):
        # delete old render before rerendering to avoid text overlap
        pg.draw.rect(self.screen, grid_colors['black'], self.rect, 0)
        # Blit the text.
        self.screen.blit(self.txt_surface, (self.rect.x+2, self.rect.y))
        # Blit the rect.
        pg.draw.rect(self.screen, self.color, self.rect, 2)

if __name__ == "__main__":
    main()
