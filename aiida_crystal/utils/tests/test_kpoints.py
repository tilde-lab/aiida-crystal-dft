#   Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida_crystal.tests.fixtures import *
from aiida_crystal.utils.kpoints import get_special_kpoints, \
    get_kpoints_path, get_kpoints_from_shrink, get_shrink_kpoints_path, construct_kpoints_path, \
    get_explicit_kpoints_path


@pytest.mark.parametrize(
    "sg_num,sg_symbol,kpoints",
    [
        (15, "C2/c", ("A", "Y", "M")),  # pyrrhotite-4c
        (205, 'Pa3', ("M", "R", "X")),  # pyrite
        (58, 'Pnnm', ("S", "T", "U", "R", "X", "Y", "Z")),  # marcasite
        (190, 'P-62c', ("M", "K", "A", "L", "H")),  # troilite
        (129, 'P4/nmm', ("M", "R", "A", "X", "Z")),  # mackinawite
        (227, 'Fd3m', ("X", "L", "W"))  # greigite
    ])
def test_get_special_kpoints(sg_num, sg_symbol, kpoints):
    for kpoint in kpoints:
        assert kpoint in get_special_kpoints(sg_symbol, sg_num)


def test_get_kpoints_path(test_structure_data):
    points, path = get_kpoints_path(test_structure_data)
    assert "GAMMA" in points
    assert ["GAMMA", "L"] in path


def test_get_shrink_kpoints_path(test_structure_data):
    shrink, points, path = get_shrink_kpoints_path(test_structure_data)
    assert shrink == 8
    assert points['GAMMA'] == [0, 0, 0]
    assert len(path) == 6


def test_get_kpoints_from_shrink():
    path = [[[0, 0, 0], [0, 4, 6]]]
    assert get_kpoints_from_shrink(path, 12) == [[[0, 0, 0], [0, 1./3, 0.5]]]
