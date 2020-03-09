"""
A test of pycrystal-based output parser
"""

import os
# from pprint import pprint
from aiida_crystal_dft.io.pycrystal.out import OutFileParser
from aiida_crystal_dft.tests import TEST_DIR


def test_out():
    """A test of parsing out file"""
    out_file = os.path.join(TEST_DIR, 'output_files', 'mgo_sto3g', 'opt', 'crystal.out')
    parser = OutFileParser(out_file)
    res = parser.get_parameters()
    # from pprint import pprint
    # pprint(res)
    assert res['creator_name'] == 'CRYSTAL'
    assert res['creator_version'] == '17 1.0.1'
