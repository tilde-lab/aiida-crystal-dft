#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection PyUnresolvedReferences
from aiida_crystal_dft.tests.fixtures import *


def test_store_calc(crystal_calc_node):
    calc = crystal_calc_node()
    calc.store()
    assert calc.pk is not None
    assert calc.inputs.code.pk is not None
    assert calc.inputs.parameters.pk is not None
    assert calc.inputs.structure.pk is not None


def test_validate_input(test_crystal_code, test_structure_data, crystal_calc_parameters, test_basis_family_predefined):
    from aiida.common.extendeddicts import AttributeDict
    from aiida_crystal_dft.calculations.serial import CrystalSerialCalculation
    inputs = AttributeDict()
    with pytest.raises(ValueError):
        CrystalSerialCalculation(inputs)
    inputs.metadata = {'options': {'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1}}}
    inputs.code = test_crystal_code
    with pytest.raises(ValueError):
        CrystalSerialCalculation(inputs)
    inputs.structure = test_structure_data
    with pytest.raises(ValueError):
        CrystalSerialCalculation(inputs)
    inputs.parameters = crystal_calc_parameters
    # TODO: write schemas code checking that either basis or basis_family is present!
    # with pytest.raises(ValueError):
    #     CrystalSerialCalculation(inputs)
    # inputs.basis_family = test_basis_family_predefined
    assert CrystalSerialCalculation(inputs)


def test_prepare_for_submission(crystal_calc):
    from aiida.common.folders import SandboxFolder
    # crystal_calc.store_all()
    with SandboxFolder() as folder:
        calcinfo = crystal_calc.prepare_for_submission(folder=folder)
    assert crystal_calc._GEOMETRY_FILE_NAME in calcinfo['retrieve_list']
    assert crystal_calc._OUTPUT_FILE_NAME in calcinfo['retrieve_list']


def test_run_crystal_calculation(crystal_calc):
    from aiida.engine import run
    from aiida_crystal_dft.tests.utils import get_authinfo
    computer = crystal_calc.inputs.code.get_remote_computer()
    get_authinfo(computer)
    result = run(crystal_calc)
    assert result['output_parameters'].dict.converged_electronic
    assert result['output_parameters'].dict.energy == -7380.221696964


def test_run_properties_calculation(properties_calc):
    from aiida.engine import run
    from aiida_crystal_dft.tests.utils import get_authinfo
    computer = properties_calc.inputs.code.get_remote_computer()
    get_authinfo(computer)
    result = run(properties_calc)
