#   Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""Tests for utilities dealing with geometry
"""

from aiida_crystal_dft.utils.geometry import get_crystal_system, get_centering_code, get_spacegroup
from aiida_crystal_dft.tests.fixtures import *


@pytest.mark.parametrize(
    "sg_num,sg_symbol,centering,crystal_type",
    [
        (15, "C2/c", 4, 2),  # pyrrhotite-4c
        (205, 'Pa3', 1, 6),  # pyrite
        (58, 'Pnnm', 1, 3),  # marcasite
        (190, 'P-62c', 1, 5),  # troilite
        (129, 'P4/nmm', 1,
         4),  # mackinawite (origin choice 2) CENTRING CODE 1/1
        (227, 'Fd3m', 5, 6)  # greigite
    ])
def test_get_centering_code(sg_num, sg_symbol, centering, crystal_type):
    """Test reading centering code, from aiida_crystal17"""
    assert get_crystal_system(sg_num, as_number=True) == crystal_type
    assert get_centering_code(sg_num, sg_symbol) == centering


def test_get_spacegroup(test_ase_structure):
    """Test getting spacegroup"""
    symbol, number = get_spacegroup(test_ase_structure.get_cell(),
                                    test_ase_structure.get_scaled_positions(),
                                    test_ase_structure.get_atomic_numbers())
    assert symbol == "Fm-3m"
    assert number == 225


def test_get_primitive(test_structure_data):
    from aiida_crystal_dft.utils.geometry import to_primitive
    primitive_struct = to_primitive(test_structure_data)
    assert primitive_struct.get_composition() == {"Fe": 1, "O": 1}
