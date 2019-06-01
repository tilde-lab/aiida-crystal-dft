#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection pyUnresolvedReference
from aiida_crystal.tests.fixtures import *


def test_predefined_basis_family(aiida_profile):
    from aiida_crystal.data.basis_family import CrystalBasisFamilyData
    bf = CrystalBasisFamilyData.get_or_create('STO-3G')
    bf.store()
    bf2 = CrystalBasisFamilyData.get_or_create('STO-3G')
    assert bf2.uuid == bf.uuid
    assert bf.content() == "BASISSET\nSTO-3G\n"
    # assert bf2.content() == "BASISSET\nSTO-3G\n"
