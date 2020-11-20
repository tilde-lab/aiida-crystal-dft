#!/usr/bin/env python

""" This is a test of base workchain submission for CRYSTAL calculation
"""
import os
import yaml
from aiida.plugins import DataFactory
from aiida.engine import submit
from mpds_aiida.workflows.mpds import MPDSStructureWorkChain

cwd = os.path.dirname(__file__)
inputs = MPDSStructureWorkChain.get_builder()
with open(f'{cwd}/MgO_MPDS.yml') as f:
    inputs.workchain_options = yaml.load(f.read(), Loader=yaml.SafeLoader)

# inputs.properties_parameters = DataFactory('dict')(dict={
#         "band": {
#             "shrink": 8,
#             "k_points": 30,
#         },
#         "dos": {
#             "n_e": 100
#         }
# })
inputs.mpds_query = DataFactory('dict')(dict={
    "formulae": "MgO",
    "sgs": 225
}
)
inputs.metadata = {"label": "MgO/225"}
# noinspection PyTypeChecker
calc = submit(MPDSStructureWorkChain, **inputs)
print("submitted WorkChain; calc=WorkCalculation(PK={})".format(
    calc.pk))
