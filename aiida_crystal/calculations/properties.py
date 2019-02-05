"""
A plugin to create a properties files from CRYSTAL17 output
"""

import six
from aiida.common.utils import classproperty
from aiida.orm import DataFactory
from aiida.orm.calculation.job import JobCalculation
from aiida_crystal.validation import read_schema
from aiida_crystal.data.basis_set import get_basissets_from_structure
from aiida_crystal.io.geometry import structure_to_dict
from aiida_crystal.io.d12_write import write_input
from aiida_crystal.utils import unflatten_dict, ATOMIC_NUM2SYMBOL


ParameterData = DataFactory("parameters")


class PropertiesCalculation(JobCalculation):
    """
    AiiDA calculation plugin wrapping the runcry17 executable.

    """

    def _init_internal_params(self):  # pylint: disable=useless-super-delegation
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(PropertiesCalculation, self)._init_internal_params()

        # default input and output files
        self._DEFAULT_INPUT_FILE = 'main.d3'
        self._DEFAULT_EXTERNAL_FILE = 'fort.34'
        self._DEFAULT_OUTPUT_FILE = 'main.out'

        # parser entry point defined in setup.json
        self._default_parser = 'crystal.basic'

    @classproperty
    def settings_schema(cls):
        """get a copy of the settings schema"""
        return read_schema("settings")

    @classproperty
    def input_schema(cls):
        """get a copy of the settings schema"""
        return read_schema("inputd12")

    # pylint: disable=too-many-arguments
    @classmethod
    def prepare_and_validate(cls,
                             param_dict,
                             structure,
                             settings,
                             basis_family=None,
                             flattened=False):
        """ prepare and validate the inputs to the calculation

        :param param_dict: dict giving data to create the input .d12 file
        :param structure: the StructureData
        :param settings: StructSettingsData giving symmetry operations, etc
        :param basis_family: string of the BasisSetFamily to use
        :param flattened: whether the input dictionary is flattened
        :return: parameters
        """
        if flattened:
            param_dict = unflatten_dict(param_dict)
        # validate structure and settings
        struct_dict = structure_to_dict(structure)
        # validate parameters
        atom_props = cls._create_atom_props(struct_dict["kinds"],
                                            settings.data)
        write_input(param_dict, ["test_basis"], atom_props)
        # validate basis sets
        if basis_family:
            get_basissets_from_structure(
                structure, basis_family, by_kind=False)

        return ParameterData(dict=param_dict)

    @classmethod
    def _get_linkname_basisset_prefix(cls):
        """
        The prefix for the name of the link used for each pseudo before the kind name
        """
        return "basis_"

    @classmethod
    def get_linkname_basisset(cls, element):
        """
        The name of the link used for the basis set for atomic element 'element'.
        It appends the basis name to the basisset_prefix, as returned by the
        _get_linkname_basisset_prefix() method.

        :param element: a string for the atomic element for which we want to get the link name
        """
        if not isinstance(element, six.string_types):
            raise TypeError(
                "The parameter 'element' of _get_linkname_basisset can "
                "only be an string: {}".format(element))
        if element not in ATOMIC_NUM2SYMBOL.values():
            raise TypeError(
                "The parameter 'symbol' of _get_linkname_basisset can "
                "must be a known atomic element: {}".format(element))

        return "{}{}".format(cls._get_linkname_basisset_prefix(), element)