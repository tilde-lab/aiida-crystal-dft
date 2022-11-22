#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import os
import pytest


def test_predefined_basis_family(aiida_profile):
    from aiida.plugins import DataFactory
    basis_family_class = DataFactory('crystal_dft.basis_family')
    bf, _ = basis_family_class.get_or_create('STO-3G')
    bf2, _ = basis_family_class.get_or_create('STO-3G')
    assert bf2.uuid == bf.uuid
    assert bf.content == "BASISSET\nSTO-3G\n"
    assert bf2.content == "BASISSET\nSTO-3G\n"
    assert bf2.predefined
    with pytest.raises(ValueError):
        basis_family_class(name='STO-3G')
    with pytest.raises(ValueError):
        basis_family_class.get_or_create(name='STO-6G', basis_sets=["bs1", "bs2"])


def test_basis_family(aiida_profile, test_structure_data):
    from aiida.plugins import DataFactory
    from aiida_crystal_dft.tests import TEST_DIR
    from aiida_crystal_dft.data.basis import CrystalBasisData
    root_dir = os.path.join(TEST_DIR, "input_files", "sto3g")
    basis_files = [os.path.join(root_dir, f) for f in os.listdir(root_dir)]
    basis_sets = [CrystalBasisData.from_file(f) for f in basis_files]
    bf, _ = DataFactory('crystal_dft.basis_family').get_or_create('STO3G', basis_sets=basis_sets)
    bf2, _ = DataFactory('crystal_dft.basis_family').get_or_create('STO3G')
    assert bf.uuid == bf2.uuid
    with pytest.raises(TypeError):
        bf.add(["bs1", "bs2"])
    with pytest.raises(ValueError):
        bf.add([basis_sets[0], basis_sets[0]])
    assert len(bf.add(basis_sets)) == 0
    bf.set_structure(test_structure_data)
    assert bf.oxi_states == {"Mg": 0., "O": 0.}
    assert bf.content == """8 2
1 0 3 2.0 0.0
1 1 3 6.0 0.0
12 3
1 0 3 2.0 0.0
1 1 3 8.0 0.0
1 1 3 2.0 0.0
99 0
"""
    with pytest.raises(ValueError):
        bf.set_oxistates({"Mg": 2.})
    with pytest.raises(ValueError):
        bf.set_oxistates({"Mg": 2., "O": -1.})
    bf.set_oxistates({"Mg": 2., "O": -2.})
    assert bf.content == """8 2
1 0 3 2.0 0.0
1 1 3 8.0 0.0
12 3
1 0 3 2.0 0.0
1 1 3 8.0 0.0
1 1 3 0.0 0.0
99 0
"""
