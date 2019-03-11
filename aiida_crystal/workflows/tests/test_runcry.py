#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""Tests for runcry workchain calculations
"""

from aiida_crystal.tests.fixtures import *


def test_props_wc_run(test_crystal_code,
                      test_properties_code,
                      crystal_calc_parameters,
                      properties_calc_parameters,
                      test_structure_data,
                      test_basis):
    from aiida_crystal.workflows.runcry import RunCryWorkChain
    from aiida.orm import DataFactory
    from aiida.work import run
    inputs = RunCryWorkChain.get_builder()
    inputs.crystal_code = test_crystal_code
    inputs.properties_code = test_properties_code
    inputs.crystal_parameters = crystal_calc_parameters
    inputs.properties_parameters = properties_calc_parameters
    inputs.basis_family = DataFactory('str')('sto-3g')
    inputs.structure = test_structure_data
    inputs.options = DataFactory('parameter')(dict={
        'resources': {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1
        }
    })
    run(RunCryWorkChain, **inputs)

