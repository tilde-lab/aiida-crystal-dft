#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import os
import shutil
import tempfile
import pytest
from ase.spacegroup import crystal


@pytest.fixture
def crystal_calc(test_crystal_code, crystal_calc_parameters, test_structure_data, test_basis):
    from aiida_crystal.calculations.serial import CrystalSerialCalculation
    calc = CrystalSerialCalculation(resources={"num_machines": 1, "num_mpiprocs_per_machine": 1})
    calc.use_code(test_crystal_code)
    calc.set_computer(test_crystal_code.get_computer())
    calc.use_structure(test_structure_data)
    calc.use_parameters(crystal_calc_parameters)
    calc.use_basis(test_basis['Mg'], 'Mg')
    calc.use_basis(test_basis['O'], 'O')
    return calc


@pytest.fixture
def properties_calc(test_properties_code, properties_calc_parameters, test_wavefunction):
    from aiida_crystal.calculations.properties import PropertiesCalculation
    calc = PropertiesCalculation(resources={"num_machines": 1, "num_mpiprocs_per_machine": 1})
    calc.use_code(test_properties_code)
    calc.set_computer(test_properties_code.get_computer())
    calc.use_parameters(properties_calc_parameters)
    calc.use_wavefunction(test_wavefunction)
    return calc


@pytest.fixture
def crystal_calc_parameters():
    from aiida.orm.data.parameter import ParameterData
    return ParameterData(dict={
        "title": "MgO Bulk",
        "scf": {
            "k_points": (8, 8)
        }
    })


@pytest.fixture
def properties_calc_parameters():
    from aiida.orm.data.parameter import ParameterData
    return ParameterData(dict={
        "band": {
            "shrink": 12,
            "kpoints": 30,
            "first": 7,
            "last": 14,
            "bands": [["G", "Y"]]
        }
    })


@pytest.fixture
def test_wavefunction():
    from aiida.orm.data.singlefile import SinglefileData
    from aiida_crystal.tests import TEST_DIR
    file_name = os.path.join(TEST_DIR,
                             'input_files',
                             'mgo_sto3g_external.fort.9')
    temp_dir = tempfile.gettempdir()
    expected = os.path.join(temp_dir, "fort.9")
    shutil.copy(file_name, expected)
    yield SinglefileData(file=expected)
    os.remove(expected)


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
