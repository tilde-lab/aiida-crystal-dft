#!/usr/bin/env python

""" This is a test of base workchain submission for CRYSTAL calculation
"""
import os
import json
from mpds_client.retrieve_MPDS import MPDSDataRetrieval

from aiida.orm import DataFactory, Code
from aiida.work import submit, run
from aiida_crystal.workflows.base import BaseCrystalWorkChain as crystal_wc
from aiida_crystal.tests import TEST_DIR


inputs = crystal_wc.get_builder()
inputs.code = Code.get_from_string('crystal@torquessh')
inputs.parameters = DataFactory('parameter')(dict={
    "title": "MgO",
    "scf": {
        "k_points": (8, 8),
    }
})
inputs.basis_family = DataFactory('str')('sto-3g')
with open(os.path.join(TEST_DIR, "input_files", "MgO.json")) as f:
    data = json.load(f)

datarow = [
    data["cell_abc"],
    data["sg_n"],
    data.get("setting", None),
    data["basis_noneq"],
    data["els_noneq"]
]

atoms = MPDSDataRetrieval.compile_crystal(datarow, flavor='ase')
inputs.structure = DataFactory('structure')(ase=atoms)
inputs.options = DataFactory('parameter')(dict={
    'resources': {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1
    }
})

calc = submit(crystal_wc, **inputs)
print("submitted WorkChain; calc=WorkCalculation(PK={})".format(
    calc.dbnode.pk))

