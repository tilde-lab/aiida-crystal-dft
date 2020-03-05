#  Copyright (c)  Andrey Sobolev, 2019-2020. Distributed under MIT license, see LICENSE file.
"""
AiiDA CRYSTAL calculation plugin.
Code shared between serial and parallel CRYSTAL calculations.
"""
from abc import ABCMeta

from ase.data import chemical_symbols
from aiida.engine import CalcJob
from aiida.orm import Dict, Code, StructureData, SinglefileData, TrajectoryData, Bool
from aiida.common import CodeInfo, CalcInfo, InputValidationError
from aiida_crystal.io.d12_write import write_input
from aiida_crystal.io.f34 import Fort34
from aiida_crystal.data.basis import CrystalBasisData
from aiida_crystal.data.basis_family import CrystalBasisFamilyData
from aiida_crystal.utils.electrons import guess_oxistates


class CrystalCommonCalculation(CalcJob, metaclass=ABCMeta):
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
        spec.input('guess_oxistates', valid_type=Bool, required=False, default=Bool(False))
        spec.input('high_spin_preferred', valid_type=Bool, required=False, default=Bool(False))
        spec.input_namespace('basis', valid_type=CrystalBasisData, required=False, dynamic=True)
        spec.input('basis_family', valid_type=CrystalBasisFamilyData, required=False)

        # output nodes
        spec.output('output_structure', valid_type=StructureData, required=False)
        spec.output('output_parameters', valid_type=Dict, required=True)
        spec.output('output_wavefunction', valid_type=SinglefileData, required=False)
        spec.output('output_trajectory', valid_type=TrajectoryData, required=False)
        spec.default_output_node = 'output_parameters'

        # input, output files and parser name
        spec.input('metadata.options.input_filename', valid_type=str, default=cls._INPUT_FILE_NAME)
        spec.input('metadata.options.output_filename', valid_type=str, default=cls._OUTPUT_FILE_NAME)
        spec.input('metadata.options.parser_name', valid_type=str, default='crystal')

        # exit codes
        # 3xx - CRYSTAL errors
        spec.exit_code(300, 'ERROR_SCF_FAILED', message='SCF calculation not converged')
        spec.exit_code(301, 'ERROR_GEOMETRY_OPTIMIZATION_FAILED', message='Geometry optimization failed')
        spec.exit_code(302, 'ERROR_UNIT_CELL_NOT_NEUTRAL', message='Unit cell not neutral')
        spec.exit_code(303, 'ERROR_BASIS_SET_LINEARLY_DEPENDENT', message='Basis set linearly dependent')
        spec.exit_code(304, 'ERROR_NEIGHBOR_LIST_TOO_BIG', message='Neighbour list too large')
        spec.exit_code(305, 'ERROR_NO_G_VECTORS', message='No G-vectors left')
        spec.exit_code(306, 'ERROR_GEOMETRY_COLLAPSED', message='Collapsed geometry')
        spec.exit_code(350, 'ERROR_ALLOCATION', message='Internal memory error')
        # 4xx - other errors
        spec.exit_code(400, 'ERROR_UNKNOWN', message='Unknown error')
        spec.exit_code(401, 'ERROR_NO_RETRIEVED_FOLDER', message='The retrieved folder data node could not be accessed')

    def _validate_basis_input(self, inputdict):
        """Input schemas; returns the dict of validated data"""
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
        return validated_dict

    def _prepare_input_files(self, folder):
        basis_dict = self._validate_basis_input(dict(self.inputs))
        # create input files: d12, taking into account
        try:
            basis_dict['basis_family'].set_structure(self.inputs.structure)
            if self.inputs.guess_oxistates:
                oxi_states = guess_oxistates(self.inputs.structure)
                basis_dict['basis_family'].set_oxistates(oxi_states)
            d12_filecontent = write_input(self.inputs.parameters.get_dict(),
                                          basis_dict['basis_family'], {})
        except (AttributeError, ValueError, NotImplementedError) as err:
            raise InputValidationError(
                "an input file could not be created from the parameters: {}".
                format(err))
        with open(folder.get_abs_path(self.inputs.metadata.options.input_filename), 'w') as f:
            f.write(d12_filecontent)

        # create input files: fort.34
        with open(folder.get_abs_path(self._GEOMETRY_FILE_NAME), 'w') as f:
            Fort34(basis=basis_dict['basis_family']).from_aiida(self.inputs.structure).write(f)

    def _prepare_codeinfo(self):
        # Prepare CodeInfo object for aiida
        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdin_name = self.inputs.metadata.options.input_filename
        return codeinfo

    def _prepare_calcinfo(self, codeinfo):
        # Prepare CalcInfo object for aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        return calcinfo
