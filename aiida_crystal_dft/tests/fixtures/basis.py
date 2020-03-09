#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Pytest fixtures dealing with basis sets
"""

import os
import pytest


@pytest.fixture
def test_basis_family_predefined(aiida_profile):
    from aiida_crystal_dft.data.basis_family import CrystalBasisFamilyData
    basis_family, _ = CrystalBasisFamilyData.get_or_create('STO-3G')
    return basis_family


@pytest.fixture
def test_basis_family(aiida_profile):
    from aiida_crystal_dft.data.basis_family import CrystalBasisFamilyData
    from .. import INPUT_FILES_DIR
    path = os.path.join(INPUT_FILES_DIR, 'sto3g')
    CrystalBasisFamilyData.upload("MINIMAL", path, extension='.basis')
    basis_family, _ = CrystalBasisFamilyData.get_or_create('MINIMAL')
    return basis_family
