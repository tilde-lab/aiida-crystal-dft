#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
The module that deals with reading and parsing *.basis files
"""
from .parsers import gto_basis_parser


class BasisFile:

    def __init__(self):
        pass

    def read(self, file_name):
        """Reads basis set from file"""
        parser = gto_basis_parser()
        with open(file_name, 'r') as f:
            res = parser.parseString(f.read())
        return res.asDict()
