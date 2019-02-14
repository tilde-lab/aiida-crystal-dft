#!/usr/bin/env python

#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import os
import json
from mpds_client.retrieve_MPDS import MPDSDataRetrieval

from aiida.orm import DataFactory, Code
from aiida.common.exceptions import NotExistent

from aiida_crystal.tests import TEST_DIR
from aiida_crystal.data.basis_set import BasisSetData
from aiida_crystal.utils import unflatten_dict


upload_basisset_family = BasisSetData.upload_basisset_family
get_basis_set = BasisSetData.get_basis_group

StructureData = DataFactory('structure')
ParameterData = DataFactory('parameter')
# get code
code = Code.get_from_string('Pcrystal@torquessh')

# Prepare input parameters
params = ParameterData(dict=unflatten_dict({
    "title": "MgO",
    "scf.k_points": (8, 8),
}))

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

try:
    basis_set = get_basis_set('sto-3g')
except NotExistent:
    upload_basisset_family(
        os.path.join(TEST_DIR, "input_files", "sto3g"),
        "sto-3g",
        "minimal basis sets",
        stop_if_existing=True,
        extension=".basis")

basis_map = BasisSetData.get_basis_group_map('sto-3g')
# set up calculation
calc = code.new_calc()

# params = calc.prepare_and_validate(params, instruct, settings, "sto-3g",
#                                    True)

calc.label = "aiida_crystal test"
calc.description = "Test job submission with the aiida_crystal plugin"
calc.set_max_wallclock_seconds(3600)
calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 2})

calc.use_structure(instruct)
calc.use_parameters(params)
calc.use_basis(basis_map["Mg"], "Mg")
calc.use_basis(basis_map["O"], "O")

calc.store_all()

calc.submit()

print("submitted calculation; calc=Calculation(PK={})".format(
    calc.dbnode.pk))
