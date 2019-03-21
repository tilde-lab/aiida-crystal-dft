#!/usr/bin/env python

""" This is a test of base workchain submission for CRYSTAL properties calculation
"""

#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import os
import csv
from ast import literal_eval
from mpds_client.retrieve_MPDS import MPDSDataRetrieval

from aiida.orm import DataFactory, Code
from aiida.work import submit
from aiida_crystal.workflows.runcry import RunCryWorkChain
from aiida_crystal.tests import TEST_DIR

inputs = RunCryWorkChain.get_builder()
inputs.crystal_code = Code.get_from_string('crystal@torquessh')
inputs.properties_code = Code.get_from_string('properties@torquessh')

# Structure
mpds_file_name = os.path.join(TEST_DIR, 'input_files', 'entries.csv')

with open(mpds_file_name) as mpds_file:
    reader = csv.DictReader(mpds_file)
    data = next(reader)

inputs.crystal_parameters = DataFactory('parameter')(dict={
    "title": data['chemical_formula'],
    "scf": {
        "k_points": (8, 8),
        "dft": {
            "xc": "PBE0",
        }
    },
    "geometry": {
        "optimise": {}
    }
})
inputs.properties_parameters = DataFactory('parameter')(dict={
    "band": {
        "k_points": 30,
    },
    "newk": {
        "k_points": [6, 6]
    },
    "dos": {
        "n_e": 300,
    }
})
inputs.basis_family = DataFactory('str')('TZVP')

datarow = [
    literal_eval(data["cell_abc"]),
    int(data["sg_n"]),
    data.get("setting", None),
    literal_eval(data["basis_noneq"]),
    literal_eval(data["els_noneq"])
]

atoms = MPDSDataRetrieval.compile_crystal(datarow, flavor='ase')
inputs.structure = DataFactory('structure')(ase=atoms)

inputs.options = DataFactory('parameter')(dict={
    'resources': {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1
    }
})

calc = submit(RunCryWorkChain, **inputs)
print("submitted WorkChain; calc=WorkCalculation(PK={})".format(
    calc.dbnode.pk))
