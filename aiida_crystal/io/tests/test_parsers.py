#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Tests for pyparsing-based parsers
"""
from ..parsers import *
# noinspection PyUnresolvedReferences
from .test_d12_read import input_str


def test_geometry_parser(input_str):
    parser = d12_geometry_parser()
    res = parser.parseString(input_str)
    for r_i in res:
        print(r_i)


def test_basis_parser():
    basis = """
47 6
HAYWSC
0 1 2   8.0  1.00
 5.8231   0.5286  -0.4178
 4.8342  -1.0470   0.1120
0 1 1   1.0  1.00
 1.8530   1.0000   1.0000
0 1 1   0.0  1.00
 0.7715   1.0000   1.0000
0 1 1   0.0  1.00
 0.1200   1.0000   1.0000
0 3 3  10.0  1.00
21.3210  -0.0140
 2.6260   2.4560
 1.0070   4.6721
0 3 1   0.0  1.00
 0.3110   1.0000
    """
    parser = gto_basis_parser()
    res = parser.parseString(basis)
    assert res['ecp'][0] == "HAYWSC"
    assert res['bs'][0][0][3] == 8.
