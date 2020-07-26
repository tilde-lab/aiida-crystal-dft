#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Tests for DOS utility functions
"""
from aiida_crystal_dft.utils.dos import get_dos_projections_atoms


def test_dos_projections():
    assert get_dos_projections_atoms([5, 6, 5, 10])
