import pygame as pg
import random
import matplotlib.backends.backend_qt5agg as agg

import math
import numpy as np



def fig2surface(fig):
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    size = canvas.get_width_height()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    surface = pg.image.fromstring(raw_data, size, "RGB")
    return surface


def blit_text(surface, text, pos, width, height, font, color):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = width, height
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 1, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height


def get_dpi():
    """Get screen resolution"""
    from screeninfo import get_monitors
    for m in get_monitors():
        if m.is_primary:
            dpi = m.width / (m.width_mm / 25.4)
            return dpi


def Gaussian(mu, sigma, x):
    # calculates the probability of x for 1-dim Gaussian with mean mu and var. sigma
    return np.exp(- ((mu - x) ** 2) / (sigma ** 2) / 2.0) / math.sqrt(2.0 * math.pi * (sigma ** 2))


def resample(weights, particles, N, robotclass):
    """resample N particles with repetition and resampling probabilities proportional to the weights"""
    # resampling wheel algorithm
    new_particles = []
    i = random.sample(range(len(weights) - 1), 1)[0]
    upper_bound = 2 * max(weights)
    beta = 0
    for _ in range(N):
        beta += random.random() * upper_bound
        while weights[i] < beta:
            beta -= weights[i]
            i += 1
            i = i % len(weights)
        new = robotclass(state=(particles[i].x, particles[i].y, particles[i].orientation),
                        forward_noise=particles[i].forward_noise,
                        turning_noise=particles[i].turning_noise,
                        sense_noise=particles[i].sense_noise)
        new_particles.append(new)
    return new_particles


def heuristic(position, goal):
    """Estimation of distance from position to goal."""
    return abs(position[0]-goal[0]) + abs(position[1]-goal[1])


def search(grid, init, goal, heuristic, cost=1):
    """A* implementation. Find best path from init to goal position."""
    moves = [[-1, 0 ], [0, -1], [1, 0], [0, 1]]
    moves_char = ['^', '<', 'v','>']
    closed = [[0 for col in range(len(grid[0]))] for row in range(len(grid))]
    closed[init[0]][init[1]] = 1
    expand = [[-1 for col in range(len(grid[0]))] for row in range(len(grid))]
    result = [[' ' for col in range(len(grid[0]))] for row in range(len(grid))]
    row, col = init
    g = 0
    f = heuristic(init, goal)
    h = g+f
    open = [[h, g, row, col]]
    found = False
    resign = False
    count = 0
    # mark closest position to goal in case no path is found
    min_f = f
    min_f_pos = init.copy()

    while not found and not resign:
        if len(open) == 0:
            resign = True
        else:
            open.sort()
            next = open.pop(0)
            g = next[1]
            row = next[2]
            col = next[3]

            expand[row][col] = count
            count += 1
            if [row, col] == goal:
                found = True
            else:
                for i in range(len(moves)):
                    new_row = row + moves[i][0]
                    new_col = col + moves[i][1]
                    if 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]):
                        if not closed[new_row][new_col] and not grid[new_row][new_col]:
                            g2 = g + cost
                            f2 = heuristic([new_row, new_col], goal)
                            h2 = g2 + f2
                            if f2 <= min_f:
                                min_f = f2
                                min_f_pos = [new_row, new_col]
                            open.append([h2, g2, new_row, new_col])
                            closed[new_row][new_col] = 1
    cur_min = math.inf
    cur = goal if not resign else min_f_pos
    result[goal[0]][goal[1]] = '*'

    while cur_min > 0:
        row, col = cur
        min_n = None
        for i in range(len(moves)):
            new_row = row + moves[i][0]
            new_col = col + moves[i][1]
            if 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]) and expand[new_row][new_col] != -1:
                if expand[new_row][new_col] < cur_min:
                    cur_min = expand[new_row][new_col]
                    min_n = [new_row, new_col]
        if not min_n:
            break
        diff_row = row-min_n[0]
        diff_col = col-min_n[1]
        for move_idx, move in enumerate(moves):
            if move == [diff_row, diff_col]:
                result[min_n[0]][min_n[1]] = moves_char[move_idx]
        cur = min_n
    if resign:
        result[min_f_pos[0]][min_f_pos[1]] = '!'
    return result

