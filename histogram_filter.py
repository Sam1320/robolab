import pygame
import sys
import random
from PIL import Image

black = (0, 0, 0)
white = (200, 200, 200)
red = (255, 150, 70)
green = (128, 255, 128)
win_height = 1000
win_width = win_height
grid = ['green', 'red', 'red', 'green', 'green']
grid_colors = {'green': green, 'red': red}
n_blocks = len(grid)
cell_size = int(win_height/n_blocks)
robot_size = int(cell_size*0.5)
robot_pos = random.randint(0, n_blocks)
outline_thickness = 4
probs = [1/len(grid) for _ in grid]
measurement_probs = {'red|red': 0.6, 'green|red': 0.2, 'green|green':0.6, 'red|green': 0.2}


def main():
    global SCREEN, CLOCK, robot_pos, probs
    pygame.init()
    SCREEN = pygame.display.set_mode((win_width, cell_size))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(black)

    while True:
        drawgrid()
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                robot_pos = (robot_pos - 1) % n_blocks
            if event.key == pygame.K_RIGHT:
                robot_pos = (robot_pos + 1) % n_blocks

        pygame.display.update()


def drawgrid():
    global  probs
    robot = pygame.image.load('robotic.png')
    robot = pygame.transform.smoothscale(robot, (robot_size, robot_size))

    for i, x in enumerate(range(0, win_width, cell_size)):
        rect = pygame.Rect(x+outline_thickness, 0+outline_thickness, cell_size-outline_thickness, cell_size-outline_thickness)
        pygame.draw.rect(SCREEN, grid_colors[grid[i]], rect, 0)
        myfont = pygame.font.SysFont("monospace", 20)
        label = myfont.render(f"Prob: {probs[0]}", 1, (0, 0, 0))
        SCREEN.blit(label, [x+(cell_size/4), 0+int((3.5*cell_size/4))])
        if i == robot_pos:
            SCREEN.blit(robot,  [x+cell_size/4, 0+cell_size/4])
        # measuremet = grid[i] if random.random() < measurement_probs[f"{grid[i]}|{grid[i]}"] else 'green' if grid[i] == 'red' else 'red'
        # probs = update_probs(probs, measuremet)

def update_probs(probs, measurement):
    res = []
    for i in range(len(probs)):
        res.append(probs[i]*measurement_probs[f"{measurement}|{grid[i]}"])
    return res


main()