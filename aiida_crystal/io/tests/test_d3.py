#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida_crystal.tests.fixtures import *
from aiida_crystal.io.d3 import D3


def test_bands_writer(aiida_profile):
    data = {
        "band": {
            "shrink": 12,
            "kpoints": 30,
            "first": 7,
            "last": 14,
            "bands": [["G", "Y"]]
        }
    }
    parser = D3(data)
    expected = """BAND
CRYSTAL RUN
1 0 30 7 14 1 0
G  Y
END"""
    assert str(parser) == expected


def test_dos_writer(aiida_profile):
    data = {
        "newk": {
            "k_points": [6, 6],
        },
        "dos": {
            "n_e": 120,
            "first": 7,
            "last": 14,
            "projections_atoms": [[5], [6, 7, 10]]
        }
    }
    parser = D3(data)
    expected = """NEWK
6 6
1 0
DOSS
2 120 7 14 1 16 0
-1 5 
-3 6 7 10 
END"""
    assert str(parser) == expected


def test_d3_reader(aiida_profile):
    from aiida_crystal.tests import TEST_DIR
    d3_file = os.path.join(TEST_DIR,
                           "input_files",
                           "mgo_sto3g.d3")
    parameters = D3().read(d3_file)
    assert parameters
