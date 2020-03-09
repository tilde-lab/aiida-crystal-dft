#!/usr/bin/env python

#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida.plugins import DataFactory, Code
from aiida.orm import load_node
from aiida.orm import SinglefileData

ParameterData = DataFactory('parameter')
# get code
code = Code.get_from_string('properties@torquessh')

# Prepare input parameters
params = Dict(dict={
    "band": {
        "shrink": 12,
        "k_points": 30,
        "first": 7,
        "last": 14,
        "bands": [["G", "W"]]
    }
})

wf = load_node(13)
assert isinstance(wf, SinglefileData)

# set up calculation
calc = code.new_calc()

calc.label = "aiida_crystal_dft properties test"
calc.description = "Test properties job submission"
calc.set_max_wallclock_seconds(3600)
calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine": 1})

calc.use_parameters(params)
calc.use_wavefunction(wf)

calc.store_all()

calc.submit()

print("submitted calculation; calc=Calculation(PK={})".format(
    calc.dbnode.pk))
