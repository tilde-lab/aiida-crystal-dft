#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Tests for fort.25 reader
"""
import os
from aiida_crystal_dft.tests import TEST_DIR
from aiida_crystal_dft.io.f25 import Fort25


def test_read_bands():
    file_name = os.path.join(TEST_DIR,
                             "output_files",
                             "mgo_sto3g",
                             "fort.25")
    parser = Fort25(file_name)
    result = parser.parse()
    assert result["BAND"]
    bands = result["BAND"]
    assert bands["n_bands"] == 14
    assert bands["n_k"] == [7, 2, 8, 6, 5, 3]
    assert bands["bands"].shape == (31, 14)


def test_read_broken_path_bands():
    file_name = os.path.join(TEST_DIR,
                             "output_files",
                             "lif_broken_band_path.fort.25")
    parser = Fort25(file_name)
    result = parser.parse()
    assert result["BAND"]
    bands = result["BAND"]
    assert bands["n_bands"] == 25
    assert bands["n_k"] == [7, 2, 8, 6, 5, 3]
    assert bands["bands"].shape == (31, 25)


def test_read_negative_path_bands():
    file_name = os.path.join(TEST_DIR,
                             "output_files",
                             "negative_band_path.fort.25")
    parser = Fort25(file_name)
    result = parser.parse()
    assert result["BAND"]
    bands = result["BAND"]
    assert bands["n_bands"] == 86
    assert bands["n_k"] == [8, 5]
    assert bands["bands"].shape == (13, 86)


def test_read_dos():
    file_name = os.path.join(TEST_DIR,
                             "output_files",
                             "mgo_sto3g",
                             "fort.25")
    parser = Fort25(file_name)
    result = parser.parse()
    assert result["DOSS"]
    dos = result["DOSS"]
    assert dos["e_fermi"] == -0.146404
    assert len(dos["e"]) == 302
    assert dos["e"][0] != 0.
    assert dos["dos_up"].shape == (3, 302)
    assert dos["dos_down"] is None


def test_read_spinpolarized_dos():
    file_name = os.path.join(TEST_DIR,
                             "output_files",
                             "spinpolarized.fort.25")
    parser = Fort25(file_name)
    result = parser.parse()
    assert result["DOSS"]
    dos = result["DOSS"]
    assert dos["e_fermi"] == -0.122904
    assert len(dos["e"]) == 25002
    assert dos["dos_up"].shape == (1, 25002)
    assert dos["dos_down"].shape == (1, 25002)
