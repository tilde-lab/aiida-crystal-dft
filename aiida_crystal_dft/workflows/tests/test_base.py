"""Tests for base workflow calculation
"""

# noinspection PyUnresolvedReferences
from aiida_crystal_dft.tests.fixtures import *


def test_crystal_wc_run(test_crystal_code, crystal_calc_parameters, test_structure_data):
    from aiida_crystal_dft.workflows.base import BaseCrystalWorkChain
    from aiida.plugins import DataFactory
    from aiida.engine import run
    inputs = BaseCrystalWorkChain.get_builder()
    inputs.code = test_crystal_code
    inputs.parameters = crystal_calc_parameters
    inputs.basis_family, _ = DataFactory('crystal.basis_family').get_or_create('STO-3G')
    inputs.structure = test_structure_data
    inputs.options = DataFactory("dict")(dict={'resources':
                                               {"num_machines": 1, "num_mpiprocs_per_machine": 1},
                                               'try_oxi_if_fails': False})
    run(BaseCrystalWorkChain, **inputs)


def test_props_wc_run(test_properties_code, properties_calc_parameters, test_wavefunction):
    from aiida_crystal_dft.workflows.base import BasePropertiesWorkChain
    from aiida.plugins import DataFactory
    from aiida.engine import run
    inputs = BasePropertiesWorkChain.get_builder()
    inputs.code = test_properties_code
    inputs.parameters = properties_calc_parameters
    inputs.wavefunction = test_wavefunction
    inputs.options = DataFactory('dict')(dict={
        'resources': {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1
        }
    })
    run(BasePropertiesWorkChain, **inputs)
