import numpy as np


def line(d, w, aa):
    return np.clip(.5 + (w - np.abs(d)) / (2 * aa), 0, 1).astype(np.float32)


def cells(s, pitch, off):
    k = np.floor(s / pitch + off); f = s / pitch + off - k
    return k, (np.minimum(f, 1 - f) * pitch).astype(np.float32)


def hash2(a, b, seed):
    v = np.sin(a * 127.1 + b * 311.7 + seed * 74.7) * 43758.5453
    return (v - np.floor(v)).astype(np.float32)
