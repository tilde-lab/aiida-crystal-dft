#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_store_calc(crystal_calc_node):
    calc = crystal_calc_node
    calc.store()
    assert calc.pk is not None
    assert calc.inputs.code.pk is not None
    assert calc.inputs.parameters.pk is not None
    assert calc.inputs.structure.pk is not None


def test_validate_input(test_crystal_code, test_structure_data, crystal_calc_parameters, test_basis_family_predefined):
    from aiida.common.extendeddicts import AttributeDict
    from aiida_crystal.calculations.serial import CrystalSerialCalculation
    inputs = AttributeDict()
    with pytest.raises(ValueError):
        CrystalSerialCalculation(inputs)
    inputs.metadata = {'options': {'resources': {'tot_num_mpiprocs': 1, 'num_mpiprocs_per_machine': 1}}}
    inputs.code = test_crystal_code
    with pytest.raises(ValueError):
        CrystalSerialCalculation(inputs)
    inputs.structure = test_structure_data
    with pytest.raises(ValueError):
        CrystalSerialCalculation(inputs)
    inputs.parameters = crystal_calc_parameters
    # TODO: write validation code checking that either basis or basis_family is present!
    # with pytest.raises(ValueError):
    #     CrystalSerialCalculation(inputs)
    # inputs.basis_family = test_basis_family_predefined
    assert CrystalSerialCalculation(inputs)


def test_submit(crystal_calc):
    from aiida.common.folders import SandboxFolder
    # crystal_calc.store_all()
    with SandboxFolder() as folder:
        subfolder, script_filename = crystal_calc.prepare_for_submission(folder=folder)
        files = os.listdir(subfolder.abspath)
    assert script_filename in files
    assert crystal_calc._GEOMETRY_FILE_NAME in files
    assert crystal_calc._DEFAULT_INPUT_FILE in files
