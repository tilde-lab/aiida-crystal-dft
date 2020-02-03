#  Copyright (c)  Andrey Sobolev, 2019-2020. Distributed under MIT license, see LICENSE file.
"""
Calculations provided by aiida_crystal.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""
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
        codeinfo = self._prepare_codeinfo()
        codeinfo.withmpi = False
        # serial CRYSTAL version writes output to stdout
        codeinfo.stdout_name = self.inputs.metadata.options.output_filename

        # Prepare CalcInfo object for aiida
        calcinfo = self._prepare_calcinfo(codeinfo)
        calcinfo.retrieve_list = retrieve_list

        return calcinfo
