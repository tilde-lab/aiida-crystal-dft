#   Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_crystal_parser(crystal_calc, crystal_calc_results):
    from aiida.orm import DataFactory
    from aiida_crystal.parsers.cry_pycrystal import CrystalParser
    parser = CrystalParser(crystal_calc)
    assert crystal_calc._DEFAULT_OUTPUT_FILE in crystal_calc_results.get_folder_list()
    _, nodes = parser.parse_with_retrieved({"retrieved": crystal_calc_results})
    nodes = dict(nodes)
    # wavefunction tests
    assert parser._linkname_wavefunction in nodes
    assert isinstance(nodes[parser._linkname_wavefunction], DataFactory("singlefile"))
    # output parameter tests
    assert parser._linkname_parameters in nodes
    assert isinstance(nodes[parser._linkname_parameters], DataFactory("parameter"))
    assert nodes[parser._linkname_parameters].dict.energy == -7380.2216063748
