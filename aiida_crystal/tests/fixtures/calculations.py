#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import pytest


@pytest.fixture
def crystal_calc(new_code):
    from aiida_crystal.calculations.serial import CrystalSerialCalculation
    calc = CrystalSerialCalculation()
    calc.use_code(new_code)
    calc.set_computer(new_code.get_computer())
    # noinspection PyDeprecation
    calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 1})
    return calc

