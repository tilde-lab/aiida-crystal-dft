#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *
from aiida_crystal.io.d3 import D3


def test_band_pass(aiida_profile):
    data = {
        "band": {
            "shrink": 12,
            "kpoints": 30,
            "first": 7,
            "last": 14,
            "bands": [["G", "W"]]
        },
    }
    parser = D3(data)
    expected = """BAND
CRYSTAL RUN
1 0 30 7 14 1 0
G  W
END"""
    assert str(parser) == expected


def test_dos_pass(aiida_profile):
    data = {
        "newk": {
            "kpoints": [12, 12],
        },
        "dos": {
            "n_e": 30,
            "first": 7,
            "last": 14,
            "projections_atoms": [[1], [2]]
        },
    }
    parser = D3(data)
    print(parser)
    expected = """NEWK
12 12
1 0
DOSS
2 30 7 14 1 16 0
-1 1 
-1 2 
END"""
    assert str(parser) == expected
