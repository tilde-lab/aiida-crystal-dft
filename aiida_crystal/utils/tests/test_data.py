#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.
"""
Tests for data helper utils
"""


def test_electronic_config():
    from aiida_crystal.utils.data import electronic_config
    assert electronic_config("Br") == [2, 2, 6, 2, 6, 2, 10, 5]
    assert electronic_config("K") == [2, 2, 6, 2, 6, 1]
