"""
AiiDA CRYSTAL calculation plugin.
Code shared between serial and parallel CRYSTAL calculations.
"""

import six
from ase.data import chemical_symbols
from aiida.engine import CalcJob
from aiida.orm import Dict, Code, StructureData, SinglefileData, TrajectoryData
from aiida.common import InputValidationError
from aiida_crystal.data.basis_set import BasisSetData
from aiida_crystal.data.basis_family import CrystalBasisFamilyData


class CrystalCommonCalculation(CalcJob):
    """
    AiiDA calculation plugin for CRYSTAL code. As there're two different executables for serial and
    parallel version, we should provide two Calculations, one for each executable version.
    CrystalCommonCalculation incorporates code shared between two calculation classes

    """
    _INPUT_FILE_NAME = 'INPUT'
    _GEOMETRY_FILE_NAME = 'fort.34'
    _OUTPUT_FILE_NAME = 'crystal.out'
    _BASIS_PREFIX = 'basis_'

    @classmethod
    def define(cls, spec):
        """ Define input and output ports
        """
        super(CrystalCommonCalculation, cls).define(spec)
        # input nodes
        spec.input('code', valid_type=Code)
        spec.input('structure', valid_type=StructureData, required=True)
        spec.input('parameters', valid_type=Dict, required=True)
        spec.input_namespace('basis', valid_type=BasisSetData, required=False, dynamic=True)
        spec.input('basis_family', valid_type=CrystalBasisFamilyData, required=False)
        # output nodes
        spec.output('output_structure', valid_type=StructureData, required=False)
        spec.output('output_parameters', valid_type=Dict, required=True)
        spec.output('output_wavefunction', valid_type=SinglefileData, required=False)
        spec.output('output_trajectory', valid_type=TrajectoryData, required=False)
        # input, output files and parser name
        spec.input('metadata.options.input_filename', valid_type=six.string_types, default=cls._INPUT_FILE_NAME)
        spec.input('metadata.options.output_filename', valid_type=six.string_types, default=cls._OUTPUT_FILE_NAME)
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default='crystal')
        # exit codes
        spec.exit_code(100, 'ERROR_NO_RETRIEVED_FOLDER', message='The retrieved folder data node could not be accessed')

    def _validate_basis_input(self, inputdict):
        """Input validation; returns the dict of validated data"""
        validated_dict = {}

        # basis family input
        basis_present = False
        validated_dict['basis_family'] = inputdict.pop('basis_family', None)
        if validated_dict['basis_family'] is not None:
            basis_present = True
            if not isinstance(validated_dict['basis_family'], CrystalBasisFamilyData):
                raise InputValidationError(
                    "basis_family not of type CrystalBasisFamilyData: {}".format(validated_dict['basis_family']))

        basis_inputs = [_ for _ in inputdict if _.startswith(self._BASIS_PREFIX)]
        basis_dict = {}

        if (not basis_present) and (not basis_inputs):
            raise InputValidationError('No basis sets specified for calculation!')
        for basis_name in basis_inputs:
            if basis_present:
                raise ValueError("Either basis or basis family (not both) must be present in calculation inputs")

            _, symbol = basis_name.split('_')
            if symbol not in chemical_symbols:
                raise InputValidationError('Basis set provided for element not in periodic table: {}'.format(symbol))
            basis = inputdict.pop(basis_name)
            basis_dict[symbol] = basis
            basis_present = True
        validated_dict['basis'] = basis_dict

        # if inputdict:
        #     raise ValidationError("Unknown inputs remained after validation: {}".format(inputdict))

        return validated_dict

    # @classmethod
    # def _get_linkname_basis(cls, element):
    #     """Returns a link name for basis, one for each element"""
    #     return "{}{}".format(cls._BASIS_PREFIX, element)
