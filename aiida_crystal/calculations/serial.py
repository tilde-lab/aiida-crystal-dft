"""
Calculations provided by aiida_crystal.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""

#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida.common import CalcInfo, CodeInfo
from aiida.common import InputValidationError
from aiida_crystal.calculations.common import CrystalCommonCalculation


class CrystalSerialCalculation(CrystalCommonCalculation):

    def prepare_for_submission(self, folder):
        """
        Create input files.

            :param folder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
        """
        retrieve_list = [
            self._GEOMETRY_FILE_NAME,
            self.inputs.metadata.options.output_filename,
            'fort.9',
            'fort.87']
        # write input files
        self._prepare_input_files(folder)

        # Prepare CodeInfo object for aiida
        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.withmpi = False
        codeinfo.stdin_name = self.inputs.metadata.options.input_filename
        # serial CRYSTAL version writes output to stdout
        codeinfo.stdout_name = self.inputs.metadata.options.output_filename

        # Prepare CalcInfo object for aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = retrieve_list
        calcinfo.local_copy_list = []

        return calcinfo
