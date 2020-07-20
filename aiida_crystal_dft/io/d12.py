"""A reader and writer for CRYSTAL d12 input file
"""
#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.

from aiida_crystal_dft.schemas import validate_with_json
from aiida_crystal_dft.schemas.jinja import get_template
from aiida_crystal_dft.data import CrystalBasisFamilyData


class D12(object):
    """A reader and writer of INPUT (or input.d12) CRYSTAL file"""

    def __init__(self, parameters=None, basis=None):
        self._input = None
        if parameters is not None:
            self.use_parameters(parameters)
        self._basis = None
        if basis is not None:
            self.use_basis(basis)
        # geometry is EXTERNAL

    def read(self, f):
        raise NotImplementedError

    def __str__(self):
        if self._input is None:
            raise ValueError("Can not make input file out of empty dict")
        template = get_template('d12.j2')
        render = template.render(basis=self._basis, **self._input)
        return '\n'.join([s.strip() for s in render.split('\n') if s.strip()]) + '\n'

    def write(self):
        """Writing input to file"""
        if self._input is None:
            raise ValueError("No ParameterData is associated with the input")
        if self._basis is None:
            raise ValueError("No BasisSets or BasisFamily is associated with the input")

    def use_parameters(self, parameters):
        """A ParameterData (or a simple dict) to use for making INPUT"""
        input_dict = parameters if isinstance(parameters, dict) else parameters.get_dict()
        validate_with_json(input_dict, name="d12")
        self._input = input_dict

    def use_basis(self, basis):
        """A BasisSetData to use for making INPUT"""
        # a valid basis should be either BasisFamily, or the list of BasisSets
        if isinstance(basis, CrystalBasisFamilyData):
            self._basis = basis.content
        elif isinstance(basis, (list, tuple)) and all([hasattr(o, 'content') for o in basis]):
            self._basis = "\n".join([b.content for b in basis] + ["99 0\n", ])
        else:
            raise ValueError("Basis must be a BasisFamily or a list of BasisSets")
