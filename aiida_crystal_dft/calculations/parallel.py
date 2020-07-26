#   Copyright (c)  Andrey Sobolev, 2019-2020. Distributed under MIT license, see LICENSE file.
"""
A parallel version of CRYSTAL calculation
"""
from aiida_crystal_dft.calculations.common import CrystalCommonCalculation


class CrystalParallelCalculation(CrystalCommonCalculation):

    _ERROR_FILE_NAME = 'OUTPUT'

    def prepare_for_submission(self, folder):
        """
        Create input files.

            :param folder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
        """
        # CRYSTAL parallel version writes input to stderr
        retrieve_list = [
            self._GEOMETRY_FILE_NAME,
            self.inputs.metadata.options.scheduler_stderr,
            'fort.9',
            'fort.87']
        # write input files
        self._prepare_input_files(folder)

        # Prepare CodeInfo object for aiida
        codeinfo = self._prepare_codeinfo()
        codeinfo.withmpi = True
        # parallel CRYSTAL version writes output to scheduler stderr
        codeinfo.stdout_name = self.inputs.metadata.options.scheduler_stderr

        # Prepare CalcInfo object for aiida
        calcinfo = self._prepare_calcinfo(codeinfo)
        calcinfo.retrieve_list = retrieve_list

        return calcinfo
