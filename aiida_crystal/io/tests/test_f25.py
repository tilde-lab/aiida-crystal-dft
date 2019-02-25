#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Tests for fort.25 reader
"""
import os
from aiida_crystal.tests import TEST_DIR
from aiida_crystal.io.f25 import Fort25


def test_read_bands():
    file_name = os.path.join(TEST_DIR,
                             "output_files",
                             "mgo_sto3g_external.bands")
    parser = Fort25(file_name)
    result = parser.parse()
    assert result["bands"]
    bands = result["bands"]
    assert bands["n_bands"] == 8
    assert bands["n_k"] == [8, 3, 5, 6, 8]
    assert bands["bands"].shape == (30, 8)
