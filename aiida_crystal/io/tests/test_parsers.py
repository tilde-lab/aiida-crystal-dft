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
