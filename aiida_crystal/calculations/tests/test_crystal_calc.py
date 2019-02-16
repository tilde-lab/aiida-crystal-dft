#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import os
import shutil
import tempfile
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


def test_validate_input(test_code, test_structure_data, calc_parameters, test_basis):
    from aiida.common.exceptions import InputValidationError
    from aiida_crystal.calculations.serial import CrystalSerialCalculation
    calc = CrystalSerialCalculation()
    with pytest.raises(InputValidationError):
        calc._validate_input(calc.get_inputs_dict())
    calc.use_code(test_code)
    with pytest.raises(InputValidationError):
        calc._validate_input(calc.get_inputs_dict())
    calc.use_structure(test_structure_data)
    with pytest.raises(InputValidationError):
        calc._validate_input(calc.get_inputs_dict())
    calc.use_parameters(calc_parameters)
    with pytest.raises(InputValidationError):
        calc._validate_input(calc.get_inputs_dict())
    calc.use_basis(test_basis['Mg'], 'Mg')
    calc.use_basis(test_basis['O'], 'O')
    assert calc._validate_input(calc.get_inputs_dict())
    with pytest.raises(InputValidationError):
        calc.use_basis(test_basis['O'], 'XXX')
        calc._validate_input(calc.get_inputs_dict())


def test_submit(crystal_calc):
    from aiida.common.folders import Folder
    temp_dir = tempfile.mkdtemp()
    crystal_calc.store_all()
    crystal_calc.submit_test(folder=Folder(temp_dir), subfolder_name='test')
    files = os.listdir(os.path.join(temp_dir, 'test-00001'))
    assert '_aiidasubmit.sh' in files
    assert 'fort.34' in files
    assert 'INPUT' in files
    shutil.rmtree(temp_dir)
