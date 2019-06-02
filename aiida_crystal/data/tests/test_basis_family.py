#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida_crystal.tests.fixtures import *


def test_predefined_basis_family(aiida_profile):
    from aiida.orm import DataFactory
    bf = DataFactory('crystal.basis_family').get_or_create('STO-3G')
    bf2 = DataFactory('crystal.basis_family').get_or_create('STO-3G')
    assert bf2.uuid == bf.uuid
    assert bf.content == "BASISSET\nSTO-3G\n"
    assert bf2.content == "BASISSET\nSTO-3G\n"
    assert bf2.predefined
    with pytest.raises(ValueError):
        DataFactory('crystal.basis_family')(name='STO-3G')
    with pytest.raises(ValueError):
        DataFactory('crystal.basis_family').get_or_create(name='STO-6G', basis_sets=["bs1", "bs2"])

