"""
A test of pycrystal-based output parser
"""

import os
from pprint import pprint
from aiida_crystal.io.pycrystal.out import parse
from aiida_crystal.tests import TEST_DIR


def test_out():
    """A test of parsing out file"""
    out_file = os.path.join(TEST_DIR, 'output_files', 'mgo_sto3g_opt.crystal.out')
    res = parse(out_file)
    pprint(res)
    assert res
