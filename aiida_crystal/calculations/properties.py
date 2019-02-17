"""
A plugin to create a properties files from CRYSTAL17 output
"""

from aiida.common.utils import classproperty
from aiida.orm import DataFactory
from aiida.orm.calculation.job import JobCalculation
from aiida.orm.data.singlefile import SinglefileData
from aiida.common.exceptions import InputValidationError
# from aiida_crystal.validation import read_schema
# from aiida_crystal.io.geometry import structure_to_dict
# from aiida_crystal.utils import unflatten_dict, ATOMIC_NUM2SYMBOL


ParameterData = DataFactory("parameters")


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

    def _validate_input(self, inputdict):
        """Input validation; returns the dict of validated data"""
        validated_dict = {}

        try:
            validated_dict['code'] = inputdict.pop(self.get_linkname('code'))
        except KeyError:
            raise InputValidationError("No code specified for this "
                                       "calculation")

        try:
            validated_dict['structure'] = inputdict.pop(self.get_linkname('structure'))
        except KeyError:
            raise InputValidationError("No structure specified for this "
                                       "calculation")
        if not isinstance(validated_dict['structure'], StructureData):
            raise InputValidationError("structure not of type "
                                       "StructureData: {}".format(validated_dict['structure']))

        try:
            validated_dict['parameters'] = inputdict.pop(self.get_linkname('parameters'))
        except KeyError:
            raise InputValidationError("No parameters specified for this "
                                       "calculation")
        if not isinstance(validated_dict['parameters'], ParameterData):
            raise InputValidationError("parameters not of type "
                                       "ParameterData: {}".format(validated_dict['parameters']))

        # settings are optional
        validated_dict['settings'] = inputdict.pop(self.get_linkname('settings'), None)
        if validated_dict['settings'] is not None:
            if not isinstance(validated_dict['settings'], ParameterData):
                raise InputValidationError(
                    "settings not of type ParameterData: {}".format(validated_dict['settings']))

        basis_inputs = [_ for _ in inputdict if _.startswith(self._BASIS_PREFIX)]
        basis_dict = {}
        if not basis_inputs:
            raise InputValidationError('No basis sets specified for calculation!')
        for basis_name in basis_inputs:
            _, symbol = basis_name.split('_')
            if symbol not in chemical_symbols:
                raise InputValidationError('Basis set provided for element not in periodic table: {}'.format(symbol))
            basis = inputdict.pop(basis_name)
            basis_dict[symbol] = basis
        validated_dict['basis'] = basis_dict

        if inputdict:
            raise ValidationError("Unknown inputs remained after validation: {}".format(inputdict))

        return validated_dict



    def _prepare_for_submission(self, tempfolder, inputdict):
        """
        Create input files.

            :param tempfolder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
            :param inputdict: dictionary of the input nodes as they would
                be returned by get_inputs_dict
        """

