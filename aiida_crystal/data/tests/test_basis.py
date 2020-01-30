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
    basis2 = CrystalBasisData.from_file(file_name)
    assert basis.uuid == basis2.uuid
    assert basis2.element == "Mg"
    assert basis2.all_electron
    assert basis2._get_occupations() == {'s': [2.0], 'sp': [8.0, 2.0], 'd': [], 'f': []}


def test_ecp_basis(aiida_profile):
    from aiida_crystal.data.basis import CrystalBasisData
    file_name = os.path.join(TEST_DIR, "input_files", "311g", "Ag.basis")
    basis = CrystalBasisData.from_file(file_name)
    assert basis.element == "Ag"
    assert not basis.all_electron
    assert basis._get_occupations() == {'s': [], 'sp': [8.0, 1.0, 0.0], 'd': [10.0, 0.0], 'f': []}
    assert basis.content == """247 5
HAYWSC
0 1 3 8.0 1.0
4.802614   -1.435200   -0.793690
4.451282   2.087100   0.716450
1.540464   -1.067800   0.708010
0 1 1 1.0 1.0
0.599610   1.000000   1.000000
0 1 1 0.0 1.0
0.187060   1.000000   1.000000
0 3 3 10.0 1.0
3.391000   0.122831
1.599000   0.417171
0.628200   0.453388
0 3 1 0.0 1.0
0.207900   1.000000"""
