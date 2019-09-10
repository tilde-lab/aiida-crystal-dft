"""
Calculations provided by aiida_crystal.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""

#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida.common import CalcInfo, CodeInfo
from aiida.common import InputValidationError
from aiida_crystal.calculations.common import CrystalCommonCalculation
from aiida_crystal.io.d12_write import write_input
from aiida_crystal.io.f34 import Fort34


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
            'fort.9']

        basis_dict = self._validate_basis_input(dict(self.inputs))
        # create input files: d12
        try:
            # d12_filecontent = write_input(basis_dict['parameters'].get_dict(),
            #                               list(basis_dict['basis'].values()), {})
            basis_dict['basis_family'].set_structure(self.inputs.structure)
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
            Fort34().from_aiida(self.inputs.structure).write(f)

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
