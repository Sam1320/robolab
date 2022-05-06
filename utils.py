import pygame as pg
from PIL import Image
import random
# import matplotlib.backends.backend_agg as agg
import matplotlib.backends.backend_qt5agg as agg
from datatypes import RobotDiff

import math


def fig2surface(fig):
    canvas = agg.FigureCanvasAgg(fig)
    a = agg.FigureCanvasAgg.supports_blit
    # a = agg.FigureCanvasBase.supports_blit
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
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    screen = app.screens()[0]
    dpi = screen.physicalDotsPerInch()
    app.quit()
    return dpi


def Gaussian(mu, sigma, x):
    # calculates the probability of x for 1-dim Gaussian with mean mu and var. sigma
    return math.exp(- ((mu - x) ** 2) / (sigma ** 2) / 2.0) / math.sqrt(2.0 * math.pi * (sigma ** 2))


def resample(weights, particles, N):
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
        new = RobotDiff(state=(particles[i].x, particles[i].y, particles[i].orientation),
                        forward_noise=particles[i].forward_noise,
                        turning_noise=particles[i].turning_noise,
                        sense_noise=particles[i].sense_noise)
        new_particles.append(new)
    return new_particles