"""Tests for base workflow calculation
"""

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_run(test_crystal_code, crystal_calc_parameters, test_structure_data, test_basis):
    from aiida_crystal.workflows.base import BaseCrystalWorkChain
    from aiida.orm import DataFactory
    from aiida.work import run
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
