"""A reader and writer for CRYSTAL d12 input file
"""
from aiida_crystal.validation import validate_with_json


class D12(object):
    """A reader and writer of INPUT (or input.d12) CRYSTAL file"""

    def __init__(self, parameters=None, basis=None):
        self._input = None
        if parameters is not None:
            self.use_parameters(parameters)
        self._basis = None
        if basis is not None:
            self.use_basis(basis)

    def read(self, f):
        raise NotImplementedError

    def __str__(self):
        return ""

    def write(self):
        """Writing input to file"""
        if self._input is None:
            raise ValueError("No ParameterData is associated with the input")
        if self._basis is None:
            raise ValueError("No BasisSet is associated with the input")

    def use_parameters(self, parameters):
        """A ParameterData to use for making INPUT"""
        input_dict = parameters.get_dict()
        validate_with_json(parameters.get_dict(), name="d12")
        self._input = input_dict

    def use_basis(self, basis):
        """A BasisSetData to use for making INPUT"""
        self._basis = basis
