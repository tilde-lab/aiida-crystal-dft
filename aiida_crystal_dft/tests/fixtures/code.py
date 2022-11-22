#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.


import os
import pytest
from aiida_crystal_dft.tests import OUTPUT_FILES_DIR


@pytest.fixture
def mock_crystal_code(mock_code_factory):
    """Creates a mock CRYSTAL code
    """
    return mock_code_factory(
        label='Pcrystal',
        data_dir_abspath=OUTPUT_FILES_DIR,
        entry_point='crystal_dft.parallel',
        ignore_files=('_aiidasubmit.sh', )
    )


@pytest.fixture
def mock_properties_code(mock_code_factory):
    return mock_code_factory(
        label='properties',
        data_dir_abspath=OUTPUT_FILES_DIR,
        entry_point='crystal_dft.properties',
        ignore_files=('_aiidasubmit.sh', )
    )