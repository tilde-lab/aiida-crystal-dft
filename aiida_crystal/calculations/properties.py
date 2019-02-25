"""
A plugin to create a properties files from CRYSTAL17 output
"""

import shutil
from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.common.utils import classproperty
from aiida.orm.calculation.job import JobCalculation
from aiida.orm.data.parameter import ParameterData
from aiida.orm.data.singlefile import SinglefileData
from aiida.common.exceptions import ValidationError, InputValidationError
from aiida_crystal.io.d3 import D3


class PropertiesCalculation(JobCalculation):
    """
    AiiDA calculation plugin wrapping the properties executable.
    """

    def _init_internal_params(self):  # pylint: disable=useless-super-delegation
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(PropertiesCalculation, self)._init_internal_params()

        # default input and output files
        self._DEFAULT_INPUT_FILE = 'main.d3'
        self._DEFAULT_OUTPUT_FILE = 'main.out'
        self._WAVEFUNCTION_FILE = 'fort.9'

        self.retrieve_list = ["fort.25"]

        # parser entry point defined in setup.json
        self._default_parser = 'crystal.properties'

    @classproperty
    def _use_methods(cls):
        """
        Add use_* methods for calculations.

        Code below enables the usage
        my_calculation.use_parameters(my_parameters)
        """
        use_dict = JobCalculation._use_methods
        use_dict.update({
            "wavefunction": {
                'valid_types': SinglefileData,
                'additional_parameter': None,
                'linkname': 'wavefunction',
                'docstring': "Wavefunction fort.9 file"
            },
            "parameters": {
                'valid_types': ParameterData,
                'additional_parameter': None,
                'linkname': 'parameters',
                'docstring': "Parameters for .d3 input file creation"
            },
            "settings": {
                'valid_types': ParameterData,
                'additional_parameter': None,
                'linkname': 'settings',
                'docstring': "Calculation settings"
            },
        })
        return use_dict

    def _validate_input(self, input_dict):
        """Input validation; returns the dict of validated data"""
        validated_dict = {}

        try:
            validated_dict['code'] = input_dict.pop(self.get_linkname('code'))
        except KeyError:
            raise InputValidationError("No code specified for this "
                                       "calculation")

        try:
            validated_dict['wavefunction'] = input_dict.pop(self.get_linkname('wavefunction'))
        except KeyError:
            raise InputValidationError("No wavefunction specified for this "
                                       "calculation")
        if not isinstance(validated_dict['wavefunction'], SinglefileData):
            raise InputValidationError("wavefunction not of type "
                                       "SinglefileData: {}".format(validated_dict['wavefunction']))

        try:
            validated_dict['parameters'] = input_dict.pop(self.get_linkname('parameters'))
        except KeyError:
            raise InputValidationError("No parameters specified for this "
                                       "calculation")
        if not isinstance(validated_dict['parameters'], ParameterData):
            raise InputValidationError("parameters not of type "
                                       "ParameterData: {}".format(validated_dict['parameters']))
        # settings are optional
        validated_dict['settings'] = input_dict.pop(self.get_linkname('settings'), None)
        if validated_dict['settings'] is not None:
            if not isinstance(validated_dict['settings'], ParameterData):
                raise InputValidationError(
                    "settings not of type ParameterData: {}".format(validated_dict['settings']))

        if input_dict:
            raise ValidationError("Unknown inputs remained after validation: {}".format(input_dict))

        return validated_dict

    def _prepare_for_submission(self, temp_folder, input_dict):
        """
        Create input files.

            :param temp_folder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
            :param input_dict: dictionary of the input nodes as they would
                be returned by get_inputs_dict
        """
        validated_dict = self._validate_input(input_dict)
        # create input files: d3
        try:
            d3_content = D3(validated_dict["parameters"].get_dict())
            # here should tinkering with k-point path go
        except (ValueError, NotImplementedError) as err:
            raise InputValidationError(
                "an input file could not be created from the parameters: {}".
                format(err))
        with open(temp_folder.get_abs_path(self._DEFAULT_INPUT_FILE), "w") as f:
            d3_content.write(f)

        # create input files: fort.9
        shutil.copy(validated_dict["wavefunction"].get_file_abs_path(),
                    temp_folder.get_abs_path(self._WAVEFUNCTION_FILE))

        # Prepare CodeInfo object for aiida
        codeinfo = CodeInfo()
        codeinfo.code_uuid = validated_dict['code'].uuid
        codeinfo.stdin_name = self._DEFAULT_INPUT_FILE
        codeinfo.stdout_name = self._DEFAULT_OUTPUT_FILE
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
