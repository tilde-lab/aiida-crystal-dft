#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""Utility functions for facilitating working with geometry
"""
import numpy as np
# import spglib


def scale_positions(positions, cell):
    """
    Convert atomic coordinates from cartesian to fractional
    :param positions: a numpy array of Cartesian atomic coordinates
    :param cell: a numpy array of cell vectors
    :return: a numpy array of atomic coordinates scaled to cell vectors
    """
    return np.linalg.solve(cell.T, positions.T).T
