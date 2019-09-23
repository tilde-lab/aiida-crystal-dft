"""
A parallel version of CRYSTAL calculation
"""
from aiida.common import CalcInfo, CodeInfo
from aiida.common import InputValidationError
from aiida_crystal.calculations.common import CrystalCommonCalculation
from aiida_crystal.io.d12_write import write_input
from aiida_crystal.io.f34 import Fort34


class CrystalParallelCalculation(CrystalCommonCalculation):

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
            'fort.9']
        # write input files
        self._prepare_input_files(folder)

        # Prepare CodeInfo object for aiida
        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.withmpi = True
        codeinfo.stdin_name = self.inputs.metadata.options.input_filename
        # parallel CRYSTAL version writes output to scheduler stderr
        codeinfo.stdout_name = self.inputs.metadata.options.scheduler_stderr

        # Prepare CalcInfo object for aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = retrieve_list
        calcinfo.local_copy_list = []

        return calcinfo
