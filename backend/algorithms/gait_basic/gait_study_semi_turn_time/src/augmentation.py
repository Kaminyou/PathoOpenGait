import copy
import random

import numpy as np


def add_random_noise(x, mean=0, std=0.001):
    size = x.shape
    return x + np.random.normal(mean, std, size)


def add_ramdom_mask(_x, ratio=0.1):
    x = copy.deepcopy(_x)
    size = x.shape
    k = 1
    for _k in size:
        k *= _k
    num = int(k * ratio)
    mask = np.zeros(k, dtype=bool)
    mask[:num] = True
    np.random.shuffle(mask)
    mask = mask.reshape(size)
    x[mask] = 0
    return x


def weak_augment(x):
    std = random.uniform(0.00005, 0.00015)
    # x = add_random_noise(x, mean=0, std=0.0001)
    x = add_random_noise(x, mean=0, std=std)
    return x


def strong_augment(x):
    std = random.uniform(0.0005, 0.0015)
    # x = add_random_noise(x, mean=0, std=0.001)
    x = add_random_noise(x, mean=0, std=std)
    ratio = random.uniform(0.001, 0.01)
    x = add_ramdom_mask(x, ratio=ratio)
    return x
