"""
A parallel version of CRYSTAL calculation
"""
from aiida.common import CalcInfo, CodeInfo
from aiida.common import InputValidationError
from aiida_crystal.calculations.common import CrystalCommonCalculation
from aiida_crystal.io.d12_write import write_input
from aiida_crystal.io.f34 import Fort34


class CrystalParallelCalculation(CrystalCommonCalculation):

    def _init_internal_params(self):
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(CrystalParallelCalculation, self)._init_internal_params()




    def prepare_for_submission(self, folder):
        """
        Create input files.

            :param folder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
        """
        retrieve_list = [
            self._GEOMETRY_FILE_NAME,
            'fort.9'
        ]
        # CRYSTAL parallel version writes input to stderr
        self._OUTPUT_FILE_NAME = self._SCHED_ERROR_FILE

        # create input files: d12
        try:
            # d12_filecontent = write_input(validated_dict['parameters'].get_dict(),
            #                               list(validated_dict['basis'].values()), {})
            validated_dict['basis_family'].set_structure(validated_dict['structure'])
            d12_filecontent = write_input(validated_dict['parameters'].get_dict(),
                                          validated_dict['basis_family'], {})
        except (ValueError, NotImplementedError) as err:
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
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.withmpi = True
        codeinfo.stdin_name = self.inputs.metadata.options.input_filename

        # Prepare CalcInfo object for aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = retrieve_list
        calcinfo.local_copy_list = []

        return calcinfo
