#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A file with various data devoted to k-points calculations: special k-points etc.
"""
from fractions import Fraction
try:
    from math import gcd
except ImportError:
    # python < 3.5
    from fractions import gcd

from functools import reduce
from .geometry import get_lattice_type, get_spacegroup


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
    ("triclinic", "P"): {
        "R": (0.5, 0.5,	0.5),
        "T": (0.0, 0.5,	0.5),
        "U": (0.5, 0.0,	0.5),
        "V": (0.5, 0.5,	0.0),
        "X": (0.5, 0.0,	0.0),
        "Y": (0.0, 0.5,	0.0),
        "Z": (0.0, 0.0,	0.5)
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
    },

    # FIXME: below is just a stub, see https://github.com/tilde-lab/aiida-crystal-dft/issues/46
    ("orthorhombic", "A"): {
        "Z": (0.5, 0.5, 0.),
        "Y": (0.5, 0., 0.5),
        "T": (0., 0.5, 0.5)
    },
    ("orthorhombic", "C"): {
        "Z": (0.5, 0.5, 0.),
        "Y": (0.5, 0., 0.5),
        "T": (0., 0.5, 0.5)
    },
}


def get_special_kpoints(symbol, sg_number):
    """Returns a dictionary of special k-points for the given spacegroup"""
    lattice = get_lattice_type(sg_number)
    return SPECIAL_K[(lattice, symbol[0])]


def get_kpoints_path(structure):
    from aiida.plugins import DataFactory
    from aiida.tools import get_kpoints_path
    if isinstance(structure, DataFactory('structure')):
        result = get_kpoints_path(structure)["parameters"].get_dict()
        return result["point_coords"], result["path"]
    else:
        raise ValueError("structure in the call to get_kpoints_path must be of StructureData type")


def get_explicit_kpoints_path(structure, path):
    from aiida.plugins import DataFactory
    from aiida.tools import get_explicit_kpoints_path
    if isinstance(structure, DataFactory('structure')):
        return get_explicit_kpoints_path(structure, method="legacy", value=path)
    else:
        raise ValueError("structure in the call to get_kpoints_path must be of StructureData type")


def get_shrink_kpoints_path(structure):
    """Returns the path of integer numbers with shrinking factor (for properties code)"""
    points, path = get_kpoints_path(structure)
    # as points is a dictionary, get coords and labels separately
    point_labels = points.keys()
    # least common multiplier for all the denominators
    shrink = reduce(lambda x, y: x * y // gcd(x, y), [Fraction(p).limit_denominator(50).denominator
                                                      for lbl in point_labels for p in points[lbl]])
    point_coords = [[int(p*shrink) for p in points[lbl]] for lbl in point_labels]
    points = dict(zip(point_labels, point_coords))
    return shrink, points, [[points[p[0]], points[p[1]]] for p in path]


def get_kpoints_from_shrink(path, shrink):
    return [[[x/shrink for x in point] for point in segment] for segment in path]


def construct_kpoints_path(cell, path, shrink, k_number, symprec=None):
    """
    Constructs a path description value that can be used for getting explicit k-points
    :param cell: A cell (in spglib sense) for which k-points path is calculated
    :param path: a list of path segments in CRYSTAL sense
    :param shrink: shrinking factor
    :param k_number: a list of k-point numbers along path segments
    :return: the path description
    """
    # get k-points (real)
    path = get_kpoints_from_shrink(path, shrink)
    continuous = get_continuity(path)
    # symmetry information
    sg_symbol, sg_number = get_spacegroup(*cell, symprec)
    special_k = {v: k for k, v in get_special_kpoints(sg_symbol, sg_number).items()}
    special_k[(0., 0., 0.)] = 'G'  # add Gamma-point
    result = []
    # due to the differences in k-points counting along path segments in CRYSTAL and aiida
    # we have to add 1 to all the k-point numbers except for the 1st and for discontinuous segments
    k_number[1:] = [x + int(cont) for x, cont in zip(k_number[1:], continuous)]
    for (p1, p2), n_k in zip(path, k_number):
        # TODO: deal with the path of special k-points
        label1 = special_k.get(tuple(p1), str(p1))
        label2 = special_k.get(tuple(p2), str(p2))
        result.append((label1, tuple(p1), label2, tuple(p2), n_k))
    return result


def get_continuity(path):
    """Returns whether k-path is continuous for all segment junctions"""
    return [path[i][1] == p_i[0] for i, p_i in enumerate(path[1:])]
