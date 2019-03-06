#   Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""Tests for properties parser
"""

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_properties_parser(properties_calc, properties_calc_results):
    from aiida.orm import DataFactory
    from aiida_crystal.parsers.properties import PropertiesParser
    parser = PropertiesParser(properties_calc)
    assert properties_calc._PROPERTIES_FILE in properties_calc_results.get_folder_list()
    _, nodes = parser.parse_with_retrieved({"retrieved": properties_calc_results})
    nodes = dict(nodes)
    assert nodes
    # bands tests
    assert parser._linkname_bands in nodes
    assert isinstance(nodes[parser._linkname_bands], DataFactory("array.bands"))
    assert nodes[parser._linkname_bands].get_kpoints().shape == (30, 3)
    # dos tests
    assert parser._linkname_dos in nodes
    assert isinstance(nodes[parser._linkname_dos], DataFactory("array"))
    assert nodes[parser._linkname_dos].get_arraynames() == ["dos", ]
    assert nodes[parser._linkname_dos].get_shape("dos") == (4, 102)
