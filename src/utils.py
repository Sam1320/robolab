from copy import deepcopy

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


def a_star_search(grid, init, goal, heuristic, cost=1, return_path_coords=False):
    """A* implementation. Find best path from init to goal position.
    Returns grid with arrows representing the path from start to goal"""
    moves = [[-1, 0], [0, -1], [1, 0], [0, 1]]
    moves_char = ['^', '<', 'v','>']
    result = [[' ' for col in range(len(grid[0]))] for row in range(len(grid))]
    path_coords = []
    expand, resign, min_f_pos = get_expansion_grid(grid, init, goal, heuristic, cost=1)
    cur_min = math.inf
    cur = goal if not resign else min_f_pos
    if return_path_coords:
        path_coords.append(cur)
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
                if return_path_coords:
                    path_coords.append(min_n)
        cur = min_n
    if resign:
        result[min_f_pos[0]][min_f_pos[1]] = '!'
    result[init[0]][init[1]] = 'S'
    if return_path_coords:
        path_coords.reverse()
        return result, path_coords
    return result, resign


def get_expansion_grid(grid, init, goal, heuristic, cost=1):
    moves = [[-1, 0], [0, -1], [1, 0], [0, 1]]
    closed = [[0 for col in range(len(grid[0]))] for row in range(len(grid))]
    closed[init[0]][init[1]] = 1
    expand = [[-1 for col in range(len(grid[0]))] for row in range(len(grid))]
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
    return expand, resign, min_f_pos


def dynamic_programming_search(grid, goal, cost=1):
    """Dynamic Programming implementation. Find best path from all positions to goal position.
    Returns grid with arrows representing path from each position to goal"""
    moves = [[-1, 0 ], [0, -1], [1, 0], [0, 1]]
    moves_char = ['^', '<', 'v','>']
    value = [[99 for row in range(len(grid[0]))] for col in range(len(grid))]
    result = [[' ' for col in range(len(grid[0]))] for row in range(len(grid))]

    change = True

    while change:
        change = False
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                if goal[0] == x and goal[1] == y:
                    if value[x][y] > 0:
                        value[x][y] = 0
                        change = True

                elif grid[x][y] == 0:
                    for a in range(len(moves)):
                        x2 = x + moves[a][0]
                        y2 = y + moves[a][1]
                        if x2 >= 0 and x2 < len(grid) and y2 >= 0 and y2 < len(grid[0]) and grid[x2][y2] == 0:
                            v2 = value[x2][y2] + cost
                            if v2 < value[x][y]:
                                change = True
                                value[x][y] = v2
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if value[row][col] == 99:
                continue
            min_n = None
            cur_min = math.inf
            for i in range(len(moves)):
                new_row = row + moves[i][0]
                new_col = col + moves[i][1]
                if 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]) and value[new_row][new_col] != 99:
                    if value[new_row][new_col] < cur_min:
                        cur_min = value[new_row][new_col]
                        min_n = [new_row, new_col]
            if not min_n:
                break
            diff_row = min_n[0]-row
            diff_col = min_n[1]-col
            for move_idx, move in enumerate(moves):
                if move == [diff_row, diff_col]:
                    result[row][col] = moves_char[move_idx]
    result[goal[0]][goal[1]] = '*'
    return result


def get_arrow(orientation, move):
    """Map action commands relative to the current orientation to directions as seen from canonical position.
     orientations = 0: up; 1: left; 2: down; 3: right
     commmands = F: Forward; R: Right; L: Left
     directions = ^: up; >:right; v:down; <:left"""
    match (orientation, move):
        case (0, 'F') | (1, 'R') | (3, 'L'):
            return '^'
        case (0, 'L') | (1, 'F') | (2, 'R'):
            return '<'
        case (0, 'R')  | (2, 'L') | (3, 'F'):
            return '>'
        case (1, 'L') | (3, 'R') | (2, 'F'):
            return 'v'


def optimum_policy2D(grid, init, goal, cost):
        #TODO: change x y to col row
        """cost: [cost of right turn, cost of forward, cost of left turn]"""
        moves = [[-1, 0],  # go up
           [0, -1],  # go left
           [1, 0],  # go down
           [0, 1]]  # go right

        # action has 3 values: right turn, no turn, left turn
        action = [-1, 0, 1]
        action_name = ['R', 'F', 'L']


        value = [[[999 for facing in range(len(moves))] \
                  for col in range(len(grid[0]))] \
                 for row in range(len(grid))]
        policy = [[[' ' for facing in range(len(moves))] \
                   for col in range(len(grid[0]))] \
                  for row in range(len(grid))]
        change = True

        while change:
            change = False

            for y in range(len(grid)):
                for x in range(len(grid[0])):
                    for f in range(len(moves)):
                        if x == goal[1] and y == goal[0]:
                            if value[y][x][f] > 0:
                                value[y][x][f] = 0
                                policy[y][x][f] = '*'
                                change = True
                        elif grid[y][x] == 0:
                            for f2 in range(len(moves)):
                                x2 = x + moves[f2][1]
                                y2 = y + moves[f2][0]
                                if x2 >= 0 and x2 < len(grid[0]) and y2 >= 0 and y2 < len(grid) and grid[y2][x2] == 0:
                                    targetVal = value[y2][x2][f2]
                                    for a in range(len(action)):
                                        if (f + action[a]) % len(moves) == f2:
                                            v2 = targetVal + cost[a]
                                            if v2 < value[y][x][f]:
                                                value[y][x][f] = v2
                                                policy[y][x][f] = action_name[a]
                                                change = True

        policy2D = [[' ' for x in range(len(grid[0]))] for y in range(len(grid))]
        x = init[1]
        y = init[0]
        f = init[2]

        policy2D[y][x] = get_arrow(f, policy[y][x][f])

        while policy[y][x][f] != '*':
            if policy[y][x][f] == 'R':
                f = (f - 1) % 4
            elif policy[y][x][f] == 'L':
                f = (f + 1) % 4
            x += moves[f][1]
            y += moves[f][0]
            policy2D[y][x] = get_arrow(f, policy[y][x][f])
        policy2D[y][x] = '*'
        policy2D[init[0]][init[1]] = 'S'
        return policy2D


def interpolate_n_points(points, n):
    """Interpolate n 2D points between points[0] and points[1]"""
    result = []
    for i in range(n):
        t = i / (n - 1)
        result.append([points[0][0] * (1 - t) + points[1][0] * t,
                       points[0][1] * (1 - t) + points[1][1] * t])
    return result


def extend_path_length(path, n):
    """Extend path by n points"""
    result = []
    for i in range(len(path)-1):
        result.extend(interpolate_n_points([path[i], path[i+1]], n))
    return result


def smooth_path(path, weight_data=0.5, weight_smooth=0.1, tolerance=0.000001):
    newpath = deepcopy(path)
    while True:
        totalChange = 0.
        for i in range(len(path)):
            if i != 0 and i != (len(path) - 1):
                for dim in range(len(path[i])):
                    oldVal = newpath[i][dim]
                    newpath[i][dim] = newpath[i][dim] + \
                                      weight_data * (path[i][dim] - newpath[i][dim]) + \
                                      weight_smooth * (
                                                  newpath[i + 1][dim] + newpath[i - 1][dim] - 2 * newpath[i][
                                              dim])
                    totalChange += abs(oldVal - newpath[i][dim])
        if totalChange < tolerance:
            break
    return newpath