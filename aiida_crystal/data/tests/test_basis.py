#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
A test suite for bases
"""

import os
from aiida_crystal.tests import TEST_DIR


def test_trivial_basis(aiida_profile):
    from aiida_crystal.data.basis import CrystalBasisData
    file_name = os.path.join(TEST_DIR, "input_files", "sto3g", "sto3g_Mg.basis")
    basis = CrystalBasisData.from_file(file_name)
    assert basis.get_dict()['header'] == [12, 3]
    assert basis.element == "Mg"
    basis.store()
    basis2 = CrystalBasisData.from_file(file_name)
    assert basis.uuid == basis2.uuid
    assert basis2.element == "Mg"
    assert basis2.all_electron


def test_ecp_basis(aiida_profile):
    from aiida_crystal.data.basis import CrystalBasisData
    file_name = os.path.join(TEST_DIR, "input_files", "311g", "Ag.basis")
    basis = CrystalBasisData.from_file(file_name)
    assert basis.element == "Ag"
    assert not basis.all_electron
