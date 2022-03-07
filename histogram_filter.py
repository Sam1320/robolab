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
# probs = [1., 0, 0, 0, 0]

pHit = .7
pMiss = .2
pGood = 0.8
pOvershoot = 0.1
pUndershoot = 0.1

measurement_probs = {'red|red': pHit, 'green|red':pMiss, 'green|green':pHit, 'red|green':pMiss}
Z = ['red', 'red']

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
                action = -1
            elif event.key == pygame.K_RIGHT:
                robot_pos = (robot_pos + 1) % n_blocks
                action = 1
            # apply motion
            probs = motion_update(probs, action)

            # sample measurement according to pHit and pMiss
            good_measurement = random.random() < pHit
            measurement = grid[robot_pos] if good_measurement else ('green' if grid[robot_pos] == 'red' else 'red')
            print(f"measurement = {good_measurement}")
            # update probabilities given the color sensed
            probs = measurement_update(probs, measurement)

        pygame.display.update()


def drawgrid():
    global probs
    robot = pygame.image.load('robotic.png')
    robot = pygame.transform.smoothscale(robot, (robot_size, robot_size))

    for i, x in enumerate(range(0, win_width, cell_size)):
        rect = pygame.Rect(x+outline_thickness, 0+outline_thickness, cell_size-outline_thickness, cell_size-outline_thickness)
        pygame.draw.rect(SCREEN, grid_colors[grid[i]], rect, 0)
        myfont = pygame.font.SysFont("monospace", 20)
        label = myfont.render(f"Prob: {probs[i]}", 1, (0, 0, 0))
        SCREEN.blit(label, [x+(cell_size/4), 0+int((3.5*cell_size/4))])
        if i == robot_pos:
            SCREEN.blit(robot,  [x+cell_size/4, 0+cell_size/4])


def measurement_update(probs, measurement):
    new_probs = []
    for i in range(len(probs)):
        hit = measurement == grid[i]
        new_p = probs[i]*(hit*pHit + (1-hit)*pMiss)
        new_probs.append(new_p)
    # normalize
    new_probs = [round(i/sum(new_probs), 4) for i in new_probs]
    return new_probs


def motion_update(p, action):
    new_p = []
    for i in range(len(p)):
        # apply law of total probability. i.e. sum over all possible transitions
        t1 = pGood*p[(i-action)%len(p)]                 # the robot moved correctly
        t2 = pOvershoot * p[(i - action - 1) % len(p)]  # the robot moved one cell too much
        t3 = pUndershoot * p[i]                         # the robot did not move
        new_p.append(t1 + t2 + t3)
    return new_p

main()