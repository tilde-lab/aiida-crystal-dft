"""A reader and writer for CRYSTAL d12 input file
"""
#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.

from aiida_crystal_dft.schemas import read_schema, validate_with_json
from aiida_crystal_dft.schemas.jinja import get_template


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
        return template.render(basis=self._basis.content, **self._input)

    def write(self):
        """Writing input to file"""
        if self._input is None:
            raise ValueError("No ParameterData is associated with the input")
        if self._basis is None:
            raise ValueError("No BasisSet is associated with the input")

    def use_parameters(self, parameters):
        """A ParameterData (or a simple dict) to use for making INPUT"""
        input_dict = parameters if isinstance(parameters, dict) else parameters.get_dict()
        validate_with_json(input_dict, name="d12")
        self._input = input_dict

    def use_basis(self, basis):
        """A BasisSetData to use for making INPUT"""
        self._basis = basis
