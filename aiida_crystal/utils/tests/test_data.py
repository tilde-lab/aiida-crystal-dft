#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.
"""
Tests for data helper utils
"""


def test_electronic_config():
    from aiida_crystal.utils.data import electronic_config
    assert electronic_config("Br") == [2, 2, 6, 2, 6, 2, 10, 5]
    assert electronic_config("K") == [2, 2, 6, 2, 6, 1]
    assert electronic_config("Br", crystal_format=True) == {'s': [2, 2, 2, 2], 'p': [6, 6, 5], 'd': [10], 'f': []}
    assert electronic_config("K", crystal_format=True) == {'s': [2, 2, 2, 1], 'p': [6, 6], 'd': [], 'f': []}
    assert electronic_config("Br", crystal_format=True, sp=True) == {'s': [2], 'sp': [8, 8, 7], 'd': [10], 'f': []}
    assert electronic_config("K", crystal_format=True, sp=True) == {'s': [2], 'sp': [8, 8, 1], 'd': [], 'f': []}
    assert electronic_config("Ag", crystal_format=True, sp=True) == {
        's': [2], 'sp': [8, 8, 8, 2], 'd': [10, 9], 'f': []
    }
