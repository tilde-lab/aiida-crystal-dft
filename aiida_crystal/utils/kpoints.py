#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A file with various data devoted to k-points calculations: special k-points etc.
"""
from __future__ import division
from .geometry import get_lattice_type

# Cubic: simple: P; BC: I, FC: F;
# Orthorhombic: Primitive - P, AC: S, BC: I, FC: F
# Monoclinic: Simple: P, BC: C
# Tetragonal: Primitive: P, BC: I

SPECIAL_K = {
    ("cubic", "P"): {
        "M": (0.5, 0.5, 0),
        "R": (0.5, 0.5, 0.5),
        "X": (0, 0.5, 0)
    },
    ("cubic", "F"): {
        "X": (0.5, 0, 0.5),
        "L": (0.5, 0.5, 0.5),
        "W": (0.5, 0.25, 0.75)
    },
    ("cubic", "I"): {
        "H": (0.5, -0.5, 0.5),
        "P": (0.25, 0.25, 0.5),
        "N": (0., 0., 0.5)
    },
    ("hexagonal", "P"): {
        "M": (0.5, 0., 0.),
        "K": (1/3., 1/3., 0.),
        "A": (0., 0., 0.5),
        "L": (0.5, 0., 0.5),
        "H": (1/3., 1/3., 0.5)
    },
    ("trigonal", "P"): {
        "M": (0.5, 0., 0.),
        "K": (1 / 3., 1 / 3., 0.),
        "A": (0., 0., 0.5),
        "L": (0.5, 0., 0.5),
        "H": (1 / 3., 1 / 3., 0.5)
    },
    ("rhombohedral", "R"): {
        "T": (0.5, 0.5, -0.5),
        "F": (0., 0.5, 0.5),
        "L": (0., 0., 0.5),
    },
    ("monoclinic", "P"): {
        "A": (0.5, -0.5, 0.),
        "B": (0.5, 0., 0.),
        "C": (0., 0.5, 0.5),
        "D": (0.5, 0., 0.5),
        "E": (0.5, -0.5, 0.5),
        "Y": (0., 0.5, 0.),
        "Z": (0., 0., 0.5)
    },
    ("monoclinic", "C"): {
        "A": (0.5, 0., 0.),
        "Y": (0., 0.5, 0.5),
        "M": (0.5, 0.5, 0.5),
    },
    ("orthorhombic", "P"): {
        "S": (0.5, 0.5, 0.),
        "T": (0., 0.5, 0.5),
        "U": (0.5, 0., 0.5),
        "R": (0.5, 0.5, 0.5),
        "X": (0.5, 0., 0.),
        "Y": (0., 0.5, 0.),
        "Z": (0., 0., 0.5)
    },
    ("orthorhombic", "F"): {
        "Z": (0.5, 0.5, 0.),
        "Y": (0.5, 0., 0.5),
        "T": (1., 0.5, 0.5)
    },
    ("orthorhombic", "S"): {
        "S": (0., 0.5, 0.),
        "T": (0.5, 0.5, 0.5),
        "R": (0., 0.5, 0.5),
        "Y": (0.5, 0.5, 0.),
        "Z": (0., 0., 0.5)
    },
    ("orthorhombic", "I"): {
        "S": (0.5, 0., 0.),
        "T": (0., 0., 0.5),
        "R": (0., 0.5, 0.),
        "X": (0.5, -0.5, 0.5),
        "W": (0.25, 0.25, 0.25)
    },
    ("tetragonal", "P"): {
        "M": (0.5, 0.5, 0.),
        "R": (0., 0.5, 0.5),
        "A": (0.5, 0.5, 0.5),
        "X": (0., 0.5, 0.),
        "Z": (0., 0., 0.5),
    },
    ("tetragonal", "I"): {
        "M": (0.5, 0.5, -0.5),
        "P": (0.5, 0.5, 0.5),
        "X": (0., 0., 0.5)
    }
}


def get_special_kpoints(symbol, sg_number):
    """Returns a dictionary of special k-points for the given spacegroup"""
    lattice = get_lattice_type(sg_number)
    return SPECIAL_K[(lattice, symbol[0])]


def get_kpoints_path(structure):
    from aiida.orm import DataFactory
    from aiida.tools import get_kpoints_path
    if isinstance(structure, DataFactory('structure')):
        result = get_kpoints_path(structure)["parameters"].get_dict()
        return result["point_coords"], result["path"]
    else:
        raise ValueError("structure in the call to get_kpoints_path must be of StructureData type")


def get_explicit_kpoints_path(structure, path):
    from aiida.orm import DataFactory
    from aiida.tools import get_explicit_kpoints_path
    if isinstance(structure, DataFactory('structure')):
        return get_explicit_kpoints_path(structure, method="legacy", value=path)
    else:
        raise ValueError("structure in the call to get_kpoints_path must be of StructureData type")


def get_kpoints_from_shrink(path, shrink):
    return [[[x/shrink for x in point] for point in segment] for segment in path]
