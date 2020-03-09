#   Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""Tests for properties parser
"""

# noinspection PyUnresolvedReferences
from aiida_crystal_dft.tests.fixtures import *


def test_properties_parser(properties_calc_node):
    from aiida.plugins import DataFactory
    from aiida_crystal_dft.parsers.properties import PropertiesParser
    calc_node = properties_calc_node()
    parser = PropertiesParser(calc_node)
    parser.parse()
    nodes = parser.outputs
    assert nodes
    # bands tests
    assert parser._linkname_bands in nodes
    assert isinstance(nodes[parser._linkname_bands], DataFactory("array.bands"))
    assert nodes[parser._linkname_bands].get_kpoints().shape == (31, 3)
    # dos tests
    assert parser._linkname_dos in nodes
    assert isinstance(nodes[parser._linkname_dos], DataFactory("array"))
    assert nodes[parser._linkname_dos].get_arraynames() == ["dos", ]
    assert nodes[parser._linkname_dos].get_shape("dos") == (4, 302)
