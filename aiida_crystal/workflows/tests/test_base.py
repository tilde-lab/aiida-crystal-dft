"""Tests for base workflow calculation
"""

from aiida_crystal.tests.fixtures import *


@pytest.mark.skip
def test_crystal_wc_run(test_crystal_code, crystal_calc_parameters, test_structure_data, test_basis):
    from aiida_crystal.workflows.base import BaseCrystalWorkChain
    from aiida.plugins import DataFactory
    from aiida.engine import run
    inputs = BaseCrystalWorkChain.get_builder()
    inputs.code = test_crystal_code
    inputs.parameters = crystal_calc_parameters
    inputs.basis_family = DataFactory('str')('sto-3g')
    inputs.structure = test_structure_data
    inputs.options = DataFactory('parameter')(dict={
        'resources': {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1
        }
    })
    run(BaseCrystalWorkChain, **inputs)

@pytest.mark.skip
def test_props_wc_run(test_properties_code, properties_calc_parameters, test_wavefunction):
    from aiida_crystal.workflows.base import BasePropertiesWorkChain
    from aiida.plugins import DataFactory
    from aiida.engine import run
    inputs = BasePropertiesWorkChain.get_builder()
    inputs.code = test_properties_code
    inputs.parameters = properties_calc_parameters
    inputs.wavefunction = test_wavefunction
    inputs.options = DataFactory('parameter')(dict={
        'resources': {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1
        }
    })
    run(BasePropertiesWorkChain, **inputs)
