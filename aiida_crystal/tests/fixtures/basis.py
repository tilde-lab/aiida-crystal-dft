#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Pytest fixtures dealing with basis sets
"""

import os
import pytest


@pytest.fixture
def test_basis_family_predefined(aiida_profile):
    from aiida_crystal.data.basis_family import CrystalBasisFamilyData
    basis_family, _ = CrystalBasisFamilyData.get_or_create('STO-3G')
    return basis_family
