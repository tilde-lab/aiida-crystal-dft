#!/usr/bin/env python

import os
import json

from ase.build.supercells import make_supercell

from aiida.orm import DataFactory, Code

from aiida_crystal.tests import TEST_DIR
from aiida_crystal.data.basis_set import get_basissets_from_structure
from aiida_crystal.data.basis_set import BasisSetData

from mpds_client.retrieve_MPDS import MPDSDataRetrieval

upload_basisset_family = BasisSetData.upload_basisset_family


StructureData = DataFactory('structure')
# get code
code = Code.get_from_string('cry@torquessh')

# Prepare input parameters
params = {
    "title": "KMnF3 antiferromagnetic",
    "scf.single": "UHF",
    "scf.k_points": (4, 4),
    "scf.spinlock.SPINLOCK": (0, 15),
    "scf.numerical.TOLINTEG": (7, 7, 7, 7, 14),
    "scf.numerical.FMIXING": 30,
    "geometry.optimise.convergence.TOLDEE": 7,
    "scf.numerical.LEVSHIFT": (3, 1),
    "scf.post_scf": ["EXCHGENE", "PPAN"]
}

# Get KMnF3 crystal structure
with open(os.path.join(TEST_DIR, "input_files", "KMnF3.json")) as f:
    data = json.load(f)

datarow = [
    data["cell_abc"],
    data["sg_n"],
    data.get("setting", None),
    data["basis_noneq"],
    data["els_noneq"]
]

atoms = MPDSDataRetrieval.compile_crystal(datarow, flavor='ase')
atoms = make_supercell(atoms, [[1, 1, 0], [1, 0, 1], [0, 1, 1]])
atoms.set_tags([1, 2, 0, 0, 0, 0, 0, 0, 0, 0])
instruct = StructureData(ase=atoms)

settings = {"kinds.spin_alpha": ["Mn1"], "kinds.spin_beta": ["Mn2"]}

from aiida_crystal.workflows.symmetrise_3d_struct import run_symmetrise_3d_structure

instruct, settings = run_symmetrise_3d_structure(instruct, settings)

upload_basisset_family(
    os.path.join(TEST_DIR, "input_files", "311g"),
    "311g",
    "not so minimal basis sets",
    stop_if_existing=False,
    extension=".basis")
# basis_map = BasisSetData.get_basis_group_map("sto3g")

# set up calculation
calc = code.new_calc()

params = calc.prepare_and_validate(params, instruct, settings, "311g",
                                   True)

calc.label = "aiida_crystal test"
calc.description = "Test job submission with the aiida_crystal plugin"
calc.set_max_wallclock_seconds(3600)
calc.set_withmpi(False)
calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 1})

calc.use_parameters(params)
calc.use_structure(instruct)
calc.use_settings(settings)
calc.use_basisset_from_family("311g")

calc.store_all()

calc.submit()

print("submitted calculation; calc=Calculation(PK={})".format(
    calc.dbnode.pk))
