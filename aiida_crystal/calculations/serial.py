"""
Calculations provided by aiida_crystal.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""

#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida_crystal.calculations.common import CrystalCommonCalculation


class CrystalSerialCalculation(CrystalCommonCalculation):

    def _init_internal_params(self):
        """
        Init internal parameters at class load time
        """

        # parser entry point defined in setup.json
        self._default_parser = 'crystal'

        # output files
        self._retrieve_list = [
            self._GEOMETRY_FILE_NAME,
            self._OUTPUT_FILE_NAME,
            'fort.9'
        ]

        # reuse base class function
        super(CrystalSerialCalculation, self)._init_internal_params()

    def _prepare_for_submission(self, tempfolder, inputdict):
        """
        Create input files.

            :param tempfolder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
            :param inputdict: dictionary of the input nodes as they would
                be returned by get_inputs_dict
        """
        validated_dict = self._validate_input(inputdict)

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
        calcinfo.retrieve_list = self._retrieve_list
        calcinfo.local_copy_list = []

        return calcinfo
