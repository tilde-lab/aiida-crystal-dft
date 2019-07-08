#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_store_calc(crystal_calc):
    calc = crystal_calc
    calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 1})
    calc.store_all()
    assert calc.pk is not None
    assert calc.inp.code.pk is not None
    assert calc.inp.parameters.pk is not None
    assert calc.inp.structure.pk is not None


def test_validate_input(test_crystal_code, test_structure_data, crystal_calc_parameters, test_basis_family_predefined):
    from aiida.common.exceptions import InputValidationError
    from aiida_crystal.calculations.serial import CrystalSerialCalculation
    calc = CrystalSerialCalculation()
    with pytest.raises(InputValidationError):
        calc._validate_input(calc.get_inputs_dict())
    calc.use_code(test_crystal_code)
    with pytest.raises(InputValidationError):
        calc._validate_input(calc.get_inputs_dict())
    calc.use_structure(test_structure_data)
    with pytest.raises(InputValidationError):
        calc._validate_input(calc.get_inputs_dict())
    calc.use_parameters(crystal_calc_parameters)
    with pytest.raises(InputValidationError):
        calc._validate_input(calc.get_inputs_dict())
    calc.use_basis_family(test_basis_family_predefined)
    assert calc._validate_input(calc.get_inputs_dict())


def test_submit(crystal_calc):
    from aiida.common.folders import SandboxFolder
    crystal_calc.store_all()
    with SandboxFolder() as folder:
        subfolder, script_filename = crystal_calc.submit_test(folder=folder)
        files = os.listdir(subfolder.abspath)
    assert script_filename in files
    assert crystal_calc._GEOMETRY_FILE_NAME in files
    assert crystal_calc._DEFAULT_INPUT_FILE in files
