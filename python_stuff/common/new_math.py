import math


def lerp(a, b, p):
    return a + (b - a) * p


def gaussian_function(x, a, b, c):
    return a * math.exp(- (x - b) ** 2 / (2 * c ** 2))
