#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A test for fort.34 reader and writer
"""
import os
# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_from_ase(aiida_profile, test_ase_structure):
    from aiida_crystal.io.f34 import Fort34
    reader = Fort34().from_ase(test_ase_structure)
    assert reader.space_group == 225
    assert reader.crystal_type == 6
    assert reader.centring == 5
    assert reader.abc[0, 1] == 2.105
    assert len(reader.positions) == 2
    assert reader.atomic_numbers[0] == 12


def test_from_aiida(aiida_profile, test_structure_data):
    from aiida_crystal.io.f34 import Fort34
    reader = Fort34().from_aiida(test_structure_data)
    assert reader.space_group == 225
    assert reader.crystal_type == 6
    assert reader.centring == 5
    assert reader.abc[0, 1] == 2.105
    assert len(reader.positions) == 2
    assert reader.atomic_numbers[0] == 12


def test_read():
    from aiida_crystal.io.f34 import Fort34
    from aiida_crystal.tests import TEST_DIR
    file_name = os.path.join(TEST_DIR,
                             'input_files',
                             'mgo_sto3g_external.crystal.gui')
    reader = Fort34().read(file_name)
    assert reader.centring == 5
    assert reader.n_symops == 48
    file_name = os.path.join(TEST_DIR,
                             'output_files',
                             'mgo_sto3g_external.fort.34')
    reader = Fort34().read(file_name)
    assert reader.centring == 5
    assert reader.n_symops == 48


