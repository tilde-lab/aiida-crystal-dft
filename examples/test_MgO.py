#!/usr/bin/env python

import os
import json

from aiida.orm import DataFactory, Code
from aiida.common.exceptions import NotExistent

from aiida_crystal.tests import TEST_DIR
from aiida_crystal.data.basis_set import BasisSetData

from mpds_client.retrieve_MPDS import MPDSDataRetrieval

upload_basisset_family = BasisSetData.upload_basisset_family
get_basis_set = BasisSetData.get_basis_group

StructureData = DataFactory('structure')
# get code
code = Code.get_from_string('pcry@torquessh')

# Prepare input parameters
params = {
    "title": "MgO",
    "scf.k_points": (8, 8),
}

# Get KMnF3 crystal structure
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
instruct = StructureData(ase=atoms)

from aiida_crystal.workflows.symmetrise_3d_struct import run_symmetrise_3d_structure

instruct, settings = run_symmetrise_3d_structure(instruct, {})

try:
    basis_set = get_basis_set('sto-3g')
except NotExistent:
    upload_basisset_family(
        os.path.join(TEST_DIR, "input_files", "sto3g"),
        "sto-3g",
        "minimal basis sets",
        stop_if_existing=True,
        extension=".basis")

# set up calculation
calc = code.new_calc()

params = calc.prepare_and_validate(params, instruct, settings, "sto-3g",
                                   True)

calc.label = "aiida_crystal test"
calc.description = "Test job submission with the aiida_crystal plugin"
calc.set_max_wallclock_seconds(3600)
calc.set_withmpi(True)
calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 2})

calc.use_parameters(params)
calc.use_structure(instruct)
calc.use_settings(settings)
calc.use_basisset_from_family("sto-3g")

calc.store_all()

calc.submit()

print("submitted calculation; calc=Calculation(PK={})".format(
    calc.dbnode.pk))
