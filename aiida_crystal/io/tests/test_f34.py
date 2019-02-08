#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A test for fort.34 reader and writer
"""

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_from_ase(aiida_profile, test_ase_structure):
    from aiida_crystal.io.f34 import Fort34
    reader = Fort34().from_ase(test_ase_structure)
    assert reader.space_group == 225
    assert reader.crystal_type == 6
    assert reader.centring == 5

