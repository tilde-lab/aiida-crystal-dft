#!/usr/bin/env python

""" This is a test of base workchain submission for CRYSTAL calculation
"""

from aiida.plugins import DataFactory
from aiida.orm import Code
from aiida.engine import submit
from mpds_aiida.workflows.crystal import MPDSCrystalWorkchain


inputs = MPDSCrystalWorkchain.get_builder()
inputs.crystal_code = Code.get_from_string('Pcrystal@torquessh')
inputs.properties_code = Code.get_from_string('properties@torquessh')

inputs.crystal_parameters = DataFactory('dict')(dict={
        "title": "Crystal calc",
        "scf": {
            "k_points": (8, 8)
        },
        "geometry": {
            "optimise": {
                "type": "FULLOPTG",
                # "convergence": {"MAXCYCLE": 3},
            },
            "phonons": {
                "ir": {
                    "type": "INTCPHF"
                },
                "raman": True
            },
            "elastic_constants": {
                "type": "ELASTCON"
            }
        }
})
inputs.properties_parameters = DataFactory('dict')(dict={
        "band": {
            "shrink": 8,
            "k_points": 30,
        },
        "dos": {
            "n_e": 100
        }
})

inputs.basis_family, _ = DataFactory('crystal.basis_family').get_or_create('MINIMAL')
inputs.mpds_query = DataFactory('dict')(dict={
        "formulae": "Li3N",
        "sgs": 191
    }
)

inputs.options = DataFactory('dict')(dict={
    'need_phonons': False,
    'need_electronic_properties': False,
    'try_oxi_if_fails': True,
    'resources': {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 2
    }
    })
inputs.metadata = {"label": "Li3N/191/hP4"}

calc = submit(MPDSCrystalWorkchain, **inputs)
print("submitted WorkChain; calc=WorkCalculation(PK={})".format(
    calc.pk))
