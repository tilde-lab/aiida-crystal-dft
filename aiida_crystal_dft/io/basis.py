#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
The module that deals with reading and parsing *.basis files
"""
from ase.data import atomic_numbers
from .parsers import gto_basis_parser


class BasisFile:

    parser = gto_basis_parser()

    def __init__(self):
        self.basis_dict = {}

    def parse(self, content):
        """Reads basis set from string"""
        self.basis_dict = BasisFile.parser.parseString(content).asDict()
        return self.basis_dict

    def read(self, file_name):
        """Reads basis set from file"""
        with open(file_name, 'r') as f:
            self.basis_dict = BasisFile.parser.parseString(f.read()).asDict()
        return self.basis_dict


class BasisAdapter:

    def __init__(self, basis):
        """The class adapts either BasisFamily or a list of Basis instances"""
        from aiida_crystal_dft.data.basis_family import CrystalBasisFamilyData
        self.basis = basis
        if isinstance(basis, CrystalBasisFamilyData):
            self.basis_type = "basis_family"
        elif isinstance(basis, list) and all([hasattr(b, "content") for b in basis]):
            self.basis_type = "list"
        else:
            raise ValueError("Basis must be represented with a BasisFamily or a list of Basis instances")

    @property
    def predefined(self):
        if self.basis_type == "basis_family":
            return self.basis.predefined
        return False

    def get_basis(self, element):
        if self.basis_type == "basis_family":
            return self.basis.get_basis(element)
        number = atomic_numbers[element]
        for b in self.basis:
            ecp_add = 0 if b.all_electron else 200
            if b.content.split()[0] == str(number + ecp_add):
                return b
        raise KeyError("No basis for element {} in list".format(element))
