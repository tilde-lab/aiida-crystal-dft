#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Tests for fort.9 reader
"""
import os
import shutil
import pytest
from aiida_crystal.tests import TEST_DIR
from aiida_crystal.io.f9 import Fort9

file_name = os.path.join(TEST_DIR,
                         "output_files",
                         "mgo_sto3g_external.fort.9")


@pytest.fixture(scope="module")
def rename_file():
    expected = os.path.join(os.path.dirname(file_name),
                            "fort.9")
    shutil.copy(file_name, expected)
    yield expected
    os.remove(expected)


def test_fail():
    with pytest.raises(ValueError):
        Fort9(file_name)


def test_pass(rename_file):
    parser = Fort9(rename_file)
    cell, positions, numbers = parser.get_cell()
    assert cell.shape == (3, 3)
    assert positions.shape == (2, 3)
    assert numbers.tolist() == [12, 8]
    assert parser.get_ao_number() == 18
