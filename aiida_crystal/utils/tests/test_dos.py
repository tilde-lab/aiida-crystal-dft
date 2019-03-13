#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Tests for DOS utility functions
"""
# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *
from aiida_crystal.utils.dos import get_dos_file_projections


def test_dos_projections(test_structure_data):
    assert get_dos_file_projections(test_structure_data)
