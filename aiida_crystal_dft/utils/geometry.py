#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""Utility functions for facilitating working with geometry
"""
import numpy as np
import spglib
from ase import Atoms


SYMPREC = 1e-04

CRYSTAL_TYPE_MAP = {
    "triclinic":    1,
    "monoclinic":   2,
    "orthorhombic": 3,
    "tetragonal":   4,
    "trigonal":     5,
    "hexagonal":    5,
    "cubic":        6
}


def get_spacegroup(cell, positions, numbers, symprec=None):
    """Returns Pearson symbol and intl number corresponding to the given structure"""
    cell = (cell, positions, numbers)
    sg = spglib.get_spacegroup(cell, symprec=symprec or SYMPREC).split()
    return sg[0], int(sg[1][1:-1])


def cart2frac(positions, cell):
    """
    Convert atomic coordinates from cartesian to fractional
    :param positions: a numpy array of Cartesian atomic coordinates
    :param cell: a numpy array of cell vectors
    :return: a numpy array of atomic coordinates scaled to cell vectors
    """
    return np.linalg.solve(cell.T, positions.T).T


def frac2cart(positions, cell):
    """
    Convert atomic coordinates from fractional to cartesian
    :param positions: a numpy array of fractional atomic coordinates
    :param cell: a numpy array of cell vectors
    :return: a numpy array of atomic coordinates in Cartesian coordinate system
    """
    return np.dot(cell, positions.T).T


def get_crystal_system(sg_number, as_number=False):
    """Get the crystal system for the structure, e.g.,
    (triclinic, orthorhombic, cubic, etc.) from the space group number

    :param sg_number: the spacegroup number
    :param as_number: return the system as a number (recognized by CRYSTAL) or a str
    :return: Crystal system for structure or None if system cannot be detected.
    """
    def f(i, j):
        return i <= sg_number <= j
    cs = {
        "triclinic": (1, 2),
        "monoclinic": (3, 15),
        "orthorhombic": (16, 74),
        "tetragonal": (75, 142),
        "trigonal": (143, 167),
        "hexagonal": (168, 194),
        "cubic": (195, 230)
    }

    crystal_system = None

    for k, val in cs.items():
        if f(*val):
            crystal_system = k
            break

    if crystal_system is None:
        raise ValueError(
            "could not find crystal system of space group number: {}".format(
                sg_number))

    if as_number:
        crystal_system = CRYSTAL_TYPE_MAP[crystal_system]

    return crystal_system


def get_lattice_type(sg_number):
    """Get the lattice for the structure, e.g., (triclinic,
    orthorhombic, cubic, etc.).This is the same than the
    crystal system with the exception of the hexagonal/rhombohedral
    lattice

    :param sg_number: space group number
    :return: Lattice type for structure or None if type cannot be detected.

    """
    system = get_crystal_system(sg_number)
    if sg_number in [146, 148, 155, 160, 161, 166, 167]:
        return "rhombohedral"
    if system == "trigonal":
        return "hexagonal"

    return system


def get_centering_code(sg_number, sg_symbol):
    """get crystal centering codes, to convert from primitive to conventional

    :param sg_number: the space group number
    :param sg_symbol: the space group symbol
    :return: CRYSTAL centering code
    """
    lattice_type = get_lattice_type(sg_number)

    if "P" in sg_symbol or lattice_type == "hexagonal":
        return 1
    if lattice_type == "rhombohedral":
        # can also be P_R (if a_length == c_length in conventional cell),
        # but crystal doesn't appear to use that anyway
        return 1
    if "I" in sg_symbol:
        return 6
    if "F" in sg_symbol:
        return 5
    if "C" in sg_symbol:
        crystal_system = get_crystal_system(sg_number, as_number=False)
        if crystal_system == "monoclinic":
            return 4  # TODO this is P_C but don't know what code it is, maybe 3?
            # [[1.0, -1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        return 4
    # elif "A" in sg_symbol:
    #     return 2  # TODO check this is always correct (not in original function)

    return 1


def to_primitive(structure):
    """Returns aiida StructureData with primitive cell"""
    from aiida.orm import StructureData
    cell, positions, numbers = spglib.find_primitive(structure.get_ase())
    ase_struct = Atoms(numbers, scaled_positions=positions, cell=cell, pbc=True)
    return StructureData(ase=ase_struct)
