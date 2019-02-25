#   Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_store_calc(properties_calc):
    calc = properties_calc
    calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 1})
    calc.store_all()
    assert calc.pk is not None
    assert calc.inp.code.pk is not None
    assert calc.inp.parameters.pk is not None
    assert calc.inp.wavefunction.pk is not None

