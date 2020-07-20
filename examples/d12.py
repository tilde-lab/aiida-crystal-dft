#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.

"""
This example shows how to write .d12 file to with custom dictionary
"""

from aiida_crystal_dft.io.d12 import D12
from collections import namedtuple

basis_mg = """12 3
1 0 3 2.0 0.0
1 1 3 8.0 0.0
1 1 3 2.0 0.0"""
basis_o = """8 2
1 0 3 2.0 0.0
1 1 3 6.0 0.0"""

inputs = {"title": "Crystal calc",
          "scf": {
              "k_points": (16, 48),
              "numerical": {"TOLINTEG": (8, 8, 8, 8, 30),
                            "FMIXING": 70,
                            "SMEAR": 0.001,
                            "NOSHIFT": True}
          },
          "geometry": {
              "optimise": {
                  "type": "FULLOPTG"
              },
          }}

basis_class = namedtuple("basis", field_names="content")
basis = basis_class(content="\n".join([basis_mg, basis_o, "99 0\n"]))

d12 = D12(parameters=inputs, basis=basis)
print(d12)
