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
                             "mgo_sto3g_external.fort.25")
    parser = Fort25(file_name)
    result = parser.parse()
    assert result["BAND"]
    bands = result["BAND"]
    assert bands["n_bands"] == 8
    assert bands["n_k"] == [8, 3, 5, 6, 8]
    assert bands["bands"].shape == (30, 8)


def test_read_dos():
    file_name = os.path.join(TEST_DIR,
                             "output_files",
                             "mgo_sto3g_external.fort.25")
    parser = Fort25(file_name)
    result = parser.parse()
    assert result["DOSS"]
    dos = result["DOSS"]
    assert dos["e_fermi"] == -0.310052
    assert len(dos["e"]) == 102
    assert dos["dos"].shape == (3, 102)
