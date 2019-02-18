#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida_crystal.tests.fixtures import *
from aiida_crystal.io.d3 import D3


def test_pass(aiida_profile):
    from aiida.orm.data.parameter import ParameterData
    data = {
        "band": {
            "shrink": 12,
            "kpoints": 30,
            "first": 7,
            "last": 14,
            "bands": [["G", "Y"]]
        }
    }
    input = D3(parameters=ParameterData(dict=data))
    print(input)
    assert input
