#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import pytest
from ase.spacegroup import crystal


@pytest.fixture
def crystal_calc(test_code, calc_parameters, test_structure_data):
    from aiida_crystal.calculations.serial import CrystalSerialCalculation
    calc = CrystalSerialCalculation()
    calc.use_code(test_code)
    calc.set_computer(test_code.get_computer())
    calc.use_structure(test_structure_data)
    calc.use_parameters(calc_parameters)
    return calc


@pytest.fixture
def calc_parameters():
    from aiida.orm.data.parameter import ParameterData
    return ParameterData(dict={
        "title": "MgO Bulk",
        "scf": {
            "k_points": (8, 8)
        }
    })


@pytest.fixture
def test_ase_structure():
    # MgO
    return crystal(
        symbols=[12, 8],
        basis=[[0, 0, 0], [0.5, 0.5, 0.5]],
        spacegroup=225,
        cellpar=[4.21, 4.21, 4.21, 90, 90, 90])


@pytest.fixture
def test_structure_data(test_ase_structure):
    from aiida.orm.data.structure import StructureData
    return StructureData(ase=test_ase_structure)
