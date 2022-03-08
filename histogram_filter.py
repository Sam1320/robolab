import pygame
import sys
import random
from PIL import Image

black = (0, 0, 0)
white = (200, 200, 200)
red = (255, 150, 70)
green = (128, 255, 128)
grid_width = 8
grid_height = 8
scale = int((1/grid_width)*800)
font_size = int(scale/10)
win_height = grid_height*scale
win_width = grid_width*scale
grid = [[random.sample(['green', 'red'], 1)[0] for _ in range(grid_width)] for _ in range(grid_height)]
# grid = ['green', 'red', 'red', 'green', 'green']
grid_colors = {'green': green, 'red': red}
cell_height = int(win_height/grid_height)
cell_width = int(win_width/grid_width)
robot_size = int(cell_height*0.5)

robot_row = 0 #random.randint(0, grid_height)
robot_col = 0 #random.randint(0, grid_width)
outline_thickness = 4
n_blocks = grid_width*grid_height
# probs = [[1/n_blocks for _ in range(grid_width)] for _ in range(grid_height)]
probs = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
probs[0][0] = 1.
pHit = .9
pMiss = 0.1
pGood = .8
pOvershoot = 0.1
pUndershoot = 0.1

measurement_probs = {'red|red': pHit, 'green|red':pMiss, 'green|green':pHit, 'red|green':pMiss}
Z = ['red', 'red']

def main():
    global SCREEN, CLOCK, robot_row, robot_col, probs
    pygame.init()
    SCREEN = pygame.display.set_mode((win_width, win_height))
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
                robot_col = (robot_col - 1) % grid_width
                action = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                robot_col = (robot_col + 1) % grid_width
                action = (1, 0)
            elif event.key == pygame.K_DOWN:
                robot_row = (robot_row + 1) % grid_height
                action = (0, 1)
            elif event.key == pygame.K_UP:
                robot_row = (robot_row - 1) % grid_height
                action = (0, -1)
            # apply motion
            probs = motion_update(probs, action)

            # sample measurement according to pHit and pMiss
            good_measurement = random.random() < pHit
            measurement = grid[robot_row][robot_col] if good_measurement else ('green' if grid[0][robot_col] == 'red' else 'red')
            print(f"measurement = {good_measurement}")
            # update probabilities given the color sensed
            probs = measurement_update(probs, measurement)

        pygame.display.update()


def drawgrid():
    global probs
    robot = pygame.image.load('robotic.png')
    robot = pygame.transform.smoothscale(robot, (robot_size, robot_size))
    myfont = pygame.font.SysFont("monospace", font_size)

    for i, y in enumerate(range(0, win_height, cell_height)):
        for j, x in enumerate(range(0, win_width, cell_width)):
            rect = pygame.Rect(x+outline_thickness, y+outline_thickness, cell_width-outline_thickness, cell_height-outline_thickness)
            pygame.draw.rect(SCREEN, grid_colors[grid[i][j]], rect, 0)
            label = myfont.render(f"p: {probs[i][j]}", 1, (0, 0, 0))
            SCREEN.blit(label, [x+(cell_width/4), y+int((3.5*cell_height/4))])
            if j == robot_col and i == robot_row:
                SCREEN.blit(robot,  [x+cell_width/4, y+cell_height/4])


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

main()