#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
This example shows how to write .d12 file to with custom dictionary
"""

from aiida_crystal.io.d12_write import write_input
from collections import namedtuple

inputs = {"title": "Crystal calc",
          "scf": {
              "k_points": (8, 8)
          },
          "geometry": {
              "optimise": {
                  "type": "FULLOPTG"
              },
          }}

basis = namedtuple("basis", field_names="content")
basis.content = """8 2
1 0 3 2.0 0.0
1 1 3 6.0 0.0
12 3
1 0 3 2.0 0.0
1 1 3 8.0 0.0
1 1 3 2.0 0.0"""
print(write_input(inputs, [basis]))


