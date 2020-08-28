"""
A plugin to create a properties files from CRYSTAL17 output
"""

from aiida.common import CalcInfo, CodeInfo, InputValidationError
from aiida.engine import CalcJob
from aiida.orm import Dict, Code, SinglefileData, BandsData, ArrayData, StructureData
from aiida_crystal_dft.io.d3 import D3


class PropertiesCalculation(CalcJob):
    """
    AiiDA calculation plugin wrapping the properties executable.
    """
    _INPUT_FILE_NAME = 'main.d3'
    _OUTPUT_FILE_NAME = 'properties.out'
    _WAVEFUNCTION_FILE_NAME = 'fort.9'
    _PROPERTIES_FILE_NAME = 'fort.25'

    @classmethod
    def define(cls, spec):
        """ Define input and output ports
        """
        super(PropertiesCalculation, cls).define(spec)
        # input nodes
        spec.input('code', valid_type=Code)
        spec.input('wavefunction', valid_type=SinglefileData, required=True)
        spec.input('parameters', valid_type=Dict, required=True)
        spec.input('structure', valid_type=StructureData, required=False)
        # output nodes
        spec.output('output_bands', valid_type=BandsData, required=False)
        spec.output('output_bands_down', valid_type=BandsData, required=False)
        spec.output('output_dos', valid_type=ArrayData, required=False)
        # input, output files and parser name
        spec.input('metadata.options.input_filename', valid_type=str, default=cls._INPUT_FILE_NAME)
        spec.input('metadata.options.output_filename', valid_type=str, default=cls._OUTPUT_FILE_NAME)
        spec.input('metadata.options.parser_name', valid_type=str, default='crystal_dft.properties')
        # exit codes
        spec.exit_code(100, 'ERROR_NO_RETRIEVED_FOLDER',
                       message='The retrieved folder data node could not be accessed')

    def prepare_for_submission(self, folder):
        """
        Create input files.

            :param folder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
        """
        # create input files: d3
        structure = self.inputs.get('structure', None)
        try:
            d3_content = D3(self.inputs.parameters.get_dict(), structure)
        except (ValueError, NotImplementedError) as err:
            raise InputValidationError(
                "an input file could not be created from the parameters: {}".
                format(err))
        with folder.open(self._INPUT_FILE_NAME, "w") as f:
            d3_content.write(f)

        # create input files: fort.9
        with self.inputs.wavefunction.open(mode="rb") as f:
            folder.create_file_from_filelike(f, self._WAVEFUNCTION_FILE_NAME, mode="wb")

        # Prepare CodeInfo object for aiida
        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdin_name = self._INPUT_FILE_NAME
        codeinfo.stdout_name = self._OUTPUT_FILE_NAME
        codeinfo.withmpi = False

        # Prepare CalcInfo object for aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = [self._PROPERTIES_FILE_NAME]
        calcinfo.local_copy_list = []

        return calcinfo
