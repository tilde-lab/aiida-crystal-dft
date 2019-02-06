"""
A parallel version of CRYSTAL calculation
"""
from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida_crystal.calculations.common import CrystalCommonCalculation


class CrystalParallelCalculation(CrystalCommonCalculation):

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
        codeinfo.stdout_name = self._OUTPUT_FILE_NAME
        codeinfo.withmpi = True

        # Prepare CalcInfo object for aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = self._retrieve_list
        calcinfo.local_copy_list = []

        return calcinfo
