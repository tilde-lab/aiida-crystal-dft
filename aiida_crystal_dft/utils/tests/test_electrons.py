#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.
"""
Tests for data helper utils
"""
# noinspection PyUnresolvedReferences
from aiida_crystal_dft.tests.fixtures import *


def test_electronic_config():
    from aiida_crystal_dft.utils.electrons import electronic_config
    assert electronic_config("Br") == [2, 2, 6, 2, 6, 2, 10, 5]
    assert electronic_config("K") == [2, 2, 6, 2, 6, 1]
    assert electronic_config("Br", crystal_format=True) == {'s': [2, 2, 2, 2], 'p': [6, 6, 5], 'd': [10], 'f': []}
    assert electronic_config("K", crystal_format=True) == {'s': [2, 2, 2, 1], 'p': [6, 6], 'd': [], 'f': []}
    assert electronic_config("Br", crystal_format=True, sp=True) == {'s': [2], 'sp': [8, 8, 7], 'd': [10], 'f': []}
    assert electronic_config("K", crystal_format=True, sp=True) == {'s': [2], 'sp': [8, 8, 1], 'd': [], 'f': []}
    assert electronic_config("Ag", crystal_format=True, sp=True) == {
        's': [2], 'sp': [8, 8, 8, 2], 'd': [10, 9], 'f': []
    }


def test_guess_oxistates(test_structure_data, test_mpds_structure):
    from aiida_crystal_dft.utils.electrons import guess_oxistates
    assert guess_oxistates(test_structure_data) == {"Mg": 2, "O": -2}


@pytest.mark.skip
def test_guess_oxistates_mpds(test_mpds_structure):
    from aiida_crystal_dft.utils.electrons import guess_oxistates
    assert guess_oxistates(test_mpds_structure) == {"Er": 2, "Hg": -2}


def test_get_valence_shell():
    from aiida_crystal_dft.utils.electrons import get_valence_shell
    assert get_valence_shell("Fe") == ["d"]
    assert get_valence_shell("Fe", n=1) == ["d", "s"]
    assert get_valence_shell("Fe", n=1, vacant=True) == ["d", "p"]
    assert get_valence_shell("Be") == ["s"]
    assert get_valence_shell("Be", n=1) == ["s", "s"]
    assert get_valence_shell("Be", n=1, vacant=True) == ["s", "p"]


def test_guess_spinlock(test_structure_data):
    from aiida_crystal_dft.utils.electrons import guess_spinlock
    guess_spinlock(test_structure_data)


