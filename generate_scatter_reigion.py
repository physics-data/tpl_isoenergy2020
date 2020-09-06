# -*- coding: utf-8 -*-
# @Author: AnnaZhang
# @Date:   2020-08-28 10:29:50
# @Last Modified by:   AnnaZhang
# @Last Modified time: 2020-09-06 21:38:06
import numpy as np
import pandas as pd
import math
from math import tan, radians, pi
import random
from scipy.interpolate import interp1d
import matplotlib as plt
import matplotlib.pyplot as pyplot
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter

SCALE = 100
WIDTH = 2 * SCALE + 1
HEIGHT = 2 * SCALE + 1
SQRT2 = math.sqrt(2)


def judge_line(points_df, n_pieces):

    if_valid = 1
    # unvalid if the line is too bumping

    if max(points_df["theta"]) < (360 / n_pieces * 0.8):
        if_valid = 0
    if min(points_df["theta"]) > (360 / n_pieces * 0.2):
        if_valid = 0
    return if_valid


def judge_region(rho, theta, n_pieces=4):
    if_valid = 1
    # unvalid if arctan not in 2*pi/n
    """
    if (y / x) > tan(2 * pi / n_pieces):
        if_valid = 0
    # unvalid if too center or too far
    if (x ** 2 + y ** 2) > (SCALE ** 2):
        if_valid = 0
    if (x ** 2 + y ** 2) < ((SCALE / 2) ** 2):
        if_valid = 0
    """

    return if_valid


def gen_random_points(n_pieces=4):
    n_points = 0
    org_points_df = pd.DataFrame(columns=["rho", "theta", "x", "y"])
    while n_points < 4:
        x = random.randint(1, SCALE)
        y = random.randint(1, SCALE)
        rho = random.uniform(SCALE * SQRT2 * 0.5, SCALE * SQRT2)
        theta = random.uniform(0, 360 / n_pieces)
        x = rho * math.cos(radians(theta))
        y = rho * math.sin(radians(theta))

        # judge if in the acceptable region
        if judge_region(rho, theta, n_pieces):
            temp_df = pd.DataFrame({"rho": [rho], "theta": [theta], "x": [x], "y": [y]})
            org_points_df = org_points_df.append(temp_df)
            n_points += 1
    return org_points_df


def interp(points_df):
    x = np.array(points_df["x"]).astype(float)
    y = np.array(points_df["y"]).astype(float)
    xx = np.linspace(0, SCALE, SCALE + 1)
    f = interp1d(x, y, kind="cubic", fill_value="extrapolate")
    y = f(xx).astype(int)
    return y


def expand(interp_y):
    x = np.linspace(0, SCALE, SCALE + 1)
    y = interp_y
    line_df_upleft = pd.DataFrame({"x": -x, "y": y})
    line_df_upright = pd.DataFrame({"x": x, "y": y})
    line_df_downleft = pd.DataFrame({"x": -x, "y": -y})
    line_df_downright = pd.DataFrame({"x": x, "y": -y})
    expanded_line_df = line_df_upleft.append(line_df_upright).append(line_df_downleft).append(line_df_downright)
    return expanded_line_df


def filling(line_df):
    im = np.zeros([WIDTH, WIDTH], dtype=np.int)
    y_prev = np.array(line_df["y"])[0] + SCALE
    for row in line_df.itertuples():
        x = int(getattr(row, "x") + SCALE)
        y = getattr(row, "y") + SCALE
        if y >= 0 and y < WIDTH:
            if y_prev >= 0 and y_prev < WIDTH:
                ymin = int(min(y_prev, y))
                ymax = int(max(y_prev, y)) + 1
                im[x, ymin:ymax] = 255
                y_prev = y
            else:
                print(x, y)
                im[x, y] = 255
                y_prev = y

    return im


if __name__ == "__main__":
    n_pics = 0
    while n_pics < 100:
        fixed_points = gen_random_points()
        y = interp(fixed_points)
        line_df = expand(y)
        im = filling(line_df)

        im_blur = gaussian_filter(im, sigma=1)
        im_blur = Image.fromarray(im_blur)
        im_blur = im_blur.convert("L")
        im_blur.save(f"dos-momentum-python/{n_pics}.png", "png")
        n_pics += 1
