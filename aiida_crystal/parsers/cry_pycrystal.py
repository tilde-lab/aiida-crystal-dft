# -*- coding: utf-8 -*-
"""
Pycrystal-based parser for CRYSTAL AiiDA plugin
"""

from __future__ import absolute_import

from aiida.parsers.parser import Parser
from aiida.common import OutputParsingError
from aiida.plugins import CalculationFactory
from aiida.plugins import DataFactory
from aiida_crystal.io.pycrystal import out
from aiida_crystal.io.f34 import Fort34


class CrystalParser(Parser):
    """
    Parser class for parsing output of CRYSTAL calculation.
    """
    _linkname_structure = "output_structure"
    _linkname_parameters = "output_parameters"
    _linkname_wavefunction = "output_wavefunction"
    _linkname_trajectory = "output_trajectory"

    # pylint: disable=protected-access
    def __init__(self, calculation):
        """
        Initialize Parser instance
        """
        super(CrystalParser, self).__init__(calculation)
        calc_entry_points = ['crystal.serial',
                             'crystal.parallel'
                             ]

        self.stdout_parser = None
        self.converged_ionic = None
        self.converged_electronic = None

        calc_cls = [CalculationFactory(entry_point) for entry_point in calc_entry_points]

        # check for valid input
        if not isinstance(calculation, tuple(calc_cls)):
            raise OutputParsingError("{}: Unexpected calculation type to parse: {}".format(
                self.__class__.__name__,
                calculation.__class__.__name__
            ))
        self._nodes = []

    # pylint: disable=protected-access
    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :param retrieved: a dictionary of retrieved nodes, where
          the key is the link name
        :returns: a tuple with two values ``(bool, node_list)``,
          where:

          * ``bool``: variable to tell if the parsing succeeded
          * ``node_list``: list of new nodes to be stored in the db
            (as a list of tuples ``(link_name, node)``)
        """
        success = False
        node_list = []

        # Check that the retrieved folder is there
        try:
            out_folder = retrieved[self._calc._get_linkname_retrieved()]
        except KeyError:
            self.logger.error("No retrieved folder found")
            return success, node_list

        # Check the folder content is as expected
        # out_folder is of type FolderData here
        list_of_files = out_folder.get_folder_list()
        output_files = self._calc.retrieve_list
        # Note: set(A) <= set(B) checks whether A is a subset
        if set(output_files) <= set(list_of_files):
            pass
        else:
            self.logger.error("Not all expected output files {} were found".
                              format(output_files))

        # parameters should be parsed first, as the results
        self.add_node(self._linkname_parameters,
                      out_folder.get_abs_path(self._calc._OUTPUT_FILE_NAME),
                      self.parse_stdout)
        self.add_node(self._linkname_structure,
                      out_folder.get_abs_path(self._calc._GEOMETRY_FILE_NAME),
                      self.parse_out_structure)
        self.add_node(self._linkname_wavefunction,
                      out_folder.get_abs_path("fort.9"),
                      self.parse_out_wavefunction)
        self.add_node(self._linkname_trajectory,
                      out_folder.get_abs_path(self._calc._OUTPUT_FILE_NAME),
                      self.parse_out_trajectory)
        success = True
        return success, self._nodes

    def add_node(self, link_name, file_name, callback):
        parse_result = callback(file_name)
        if parse_result is not None:
            self._nodes.append((link_name, callback(file_name)))

    def parse_stdout(self, file_name):
        self.stdout_parser = out.OutFileParser(file_name)
        params = self.stdout_parser.get_parameters()
        # raise flag if structure (atomic and electronic) is good
        self.converged_electronic = params['converged_electronic']
        self.converged_ionic = params['converged_ionic']
        return DataFactory('parameter')(dict=params)

    def parse_out_structure(self, file_name):
        if not self.converged_ionic:
            return None
        parser = Fort34().read(file_name)
        return parser.to_aiida()

    def parse_out_wavefunction(self, file_name):
        if not self.converged_electronic:
            return None
        return DataFactory('singlefile')(file=file_name)

    def parse_out_trajectory(self, _):
        ase_structs = self.stdout_parser.get_trajectory()
        if not ase_structs:
            return None
        structs = [DataFactory('structure')(ase=struct) for struct in ase_structs]
        traj = DataFactory('array.trajectory')()
        traj.set_structurelist(structs)
        return traj
