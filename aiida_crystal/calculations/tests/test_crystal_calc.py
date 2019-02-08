#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_store_calc(crystal_calc):
    calc = crystal_calc
    calc.store_all()
    assert calc.pk is not None
    assert calc.inp.parameters.pk is not None
    assert calc.inp.structure.pk is not None
    assert calc.inp.settings.pk is not None

