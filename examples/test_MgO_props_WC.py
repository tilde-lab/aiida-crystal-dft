#!/usr/bin/env python

""" This is a test of base workchain submission for CRYSTAL properties calculation
"""

from aiida.orm import DataFactory, Code, load_node
from aiida.work import submit
from aiida_crystal.workflows.base import BasePropertiesWorkChain


inputs = BasePropertiesWorkChain.get_builder()
inputs.code = Code.get_from_string('properties@torquessh')
inputs.parameters = DataFactory('parameter')(dict={
    "band": {
        "shrink": 12,
        "kpoints": 30,
        "first": 7,
        "last": 14,
        "bands": [["G", "W"]]
    }
})

wf = load_node(13)
assert isinstance(wf, DataFactory('singlefile'))
inputs.wavefunction = wf
inputs.options = DataFactory('parameter')(dict={
    'resources': {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1
    }
})

calc = submit(BasePropertiesWorkChain, **inputs)
print("submitted WorkChain; calc=WorkCalculation(PK={})".format(
    calc.dbnode.pk))
