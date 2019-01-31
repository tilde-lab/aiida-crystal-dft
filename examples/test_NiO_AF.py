#!/usr/bin/env python

import os

from ase.spacegroup import crystal

from aiida.orm import DataFactory, Code

from aiida_crystal.tests import TEST_DIR
from aiida_crystal.data.basis_set import get_basissets_from_structure
from aiida_crystal.data.basis_set import BasisSetData

upload_basisset_family = BasisSetData.upload_basisset_family


StructureData = DataFactory('structure')
# get code
code = Code.get_from_string('cry@torquessh')

# Prepare input parameters
params = {
    "title": "NiO Bulk with AFM spin",
    "scf.single": "UHF",
    "scf.k_points": (8, 8),
    "scf.spinlock.SPINLOCK": (0, 15),
    "scf.numerical.FMIXING": 30,
    "scf.post_scf": ["PPAN"]
}

# Ni0
atoms = crystal(
    symbols=[28, 8],
    basis=[[0, 0, 0], [0.5, 0.5, 0.5]],
    spacegroup=225,
    cellpar=[4.164, 4.164, 4.164, 90, 90, 90])
atoms.set_tags([1, 1, 2, 2, 0, 0, 0, 0])
instruct = StructureData(ase=atoms)

settings = {"kinds.spin_alpha": ["Ni1"], "kinds.spin_beta": ["Ni2"]}

from aiida_crystal.workflows.symmetrise_3d_struct import run_symmetrise_3d_structure

instruct, settings = run_symmetrise_3d_structure(instruct, settings)

upload_basisset_family(
    os.path.join(TEST_DIR, "input_files", "sto3g"),
    "sto3g",
    "minimal basis sets",
    stop_if_existing=False,
    extension=".basis")
# basis_map = BasisSetData.get_basis_group_map("sto3g")

# set up calculation
calc = code.new_calc()

params = calc.prepare_and_validate(params, instruct, settings, "sto3g",
                                   True)

calc.label = "aiida_crystal test"
calc.description = "Test job submission with the aiida_crystal plugin"
calc.set_max_wallclock_seconds(3600)
calc.set_withmpi(False)
calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 1})

calc.use_parameters(params)
calc.use_structure(instruct)
calc.use_settings(settings)
calc.use_basisset_from_family("sto3g")

calc.store_all()

calc.submit()

print("submitted calculation; calc=Calculation(PK={})".format(
    calc.dbnode.pk))
