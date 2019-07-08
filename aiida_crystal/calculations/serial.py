"""
Calculations provided by aiida_crystal.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""

#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.common.exceptions import InputValidationError
from aiida_crystal.calculations.common import CrystalCommonCalculation
from aiida_crystal.io.d12_write import write_input
from aiida_crystal.io.f34 import Fort34


class CrystalSerialCalculation(CrystalCommonCalculation):

    def _init_internal_params(self):
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(CrystalSerialCalculation, self)._init_internal_params()

        self.retrieve_list = [
            self._GEOMETRY_FILE_NAME,
            self._OUTPUT_FILE_NAME,
            'fort.9'
        ]

    def _prepare_for_submission(self, tempfolder, inputdict):
        """
        Create input files.

            :param tempfolder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
            :param inputdict: dictionary of the input nodes as they would
                be returned by get_inputs_dict
        """
        validated_dict = self._validate_input(inputdict)
        # create input files: d12
        try:
            # d12_filecontent = write_input(validated_dict['parameters'].get_dict(),
            #                               list(validated_dict['basis'].values()), {})
            validated_dict['basis_family'].set_structure(validated_dict['structure'])
            d12_filecontent = write_input(validated_dict['parameters'].get_dict(),
                                          validated_dict['basis_family'], {})
        except (AttributeError, ValueError, NotImplementedError) as err:
            raise InputValidationError(
                "an input file could not be created from the parameters: {}".
                format(err))
        with open(tempfolder.get_abs_path(self._INPUT_FILE_NAME), 'w') as f:
            f.write(d12_filecontent)

        # create input files: fort.34
        with open(tempfolder.get_abs_path(self._GEOMETRY_FILE_NAME), 'w') as f:
            Fort34().from_aiida(validated_dict['structure']).write(f)

        # Prepare CodeInfo object for aiida
        codeinfo = CodeInfo()
        codeinfo.code_uuid = validated_dict['code'].uuid
        codeinfo.stdin_name = self._INPUT_FILE_NAME
        codeinfo.stdout_name = self._OUTPUT_FILE_NAME
        codeinfo.withmpi = False

        # Prepare CalcInfo object for aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = self.retrieve_list
        calcinfo.local_copy_list = []

        return calcinfo
