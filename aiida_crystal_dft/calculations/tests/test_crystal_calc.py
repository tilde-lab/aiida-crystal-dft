#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
import pytest


def test_store_calc(crystal_calc_node):
    calc = crystal_calc_node()
    calc.store()
    assert calc.pk is not None
    assert calc.inputs.code.pk is not None
    assert calc.inputs.parameters.pk is not None
    assert calc.inputs.structure.pk is not None


def test_validate_input(mock_crystal_code, test_structure_data, crystal_calc_parameters, test_basis_family_predefined):
    from aiida.common.extendeddicts import AttributeDict
    from aiida_crystal_dft.calculations.serial import CrystalSerialCalculation
    inputs = AttributeDict()
    with pytest.raises(ValueError):
        CrystalSerialCalculation(inputs)
    inputs.metadata = {'options': {'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1}}}
    inputs.code = mock_crystal_code
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


def test_prepare_for_submission(crystal_calc_inputs):
    from aiida.common.folders import SandboxFolder
    from aiida.plugins import CalculationFactory
    crystal_calc = CalculationFactory("crystal_dft.parallel")(crystal_calc_inputs)
    with SandboxFolder() as folder:
        calc_info = crystal_calc.prepare_for_submission(folder=folder)
    assert crystal_calc._GEOMETRY_FILE_NAME in calc_info['retrieve_list']
    assert crystal_calc._OUTPUT_FILE_NAME in calc_info['retrieve_list']


def test_run_crystal_calculation(crystal_calc_inputs):
    from aiida.engine import run_get_node
    from aiida.plugins import CalculationFactory
    result, node = run_get_node(CalculationFactory("crystal_dft.parallel"), **crystal_calc_inputs)
    assert node.is_finished_ok
    assert result['output_parameters'].dict.converged_electronic
    assert result['output_parameters'].dict.energy == -7380.221696964


def test_run_properties_calculation(properties_calc_inputs):
    from aiida.engine import run_get_node
    from aiida.plugins import CalculationFactory
    result, node = run_get_node(CalculationFactory("crystal_dft.properties"),
                                **properties_calc_inputs)
    assert node.is_finished_ok
