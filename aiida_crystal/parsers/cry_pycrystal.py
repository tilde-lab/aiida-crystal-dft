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
    def __init__(self, calc_node):
        """
        Initialize Parser instance
        """
        # check for valid calculation node class
        calc_entry_points = ['crystal.serial',
                             'crystal.parallel'
                             ]
        calc_cls = [CalculationFactory(entry_point).get_name() for entry_point in calc_entry_points]
        if calc_node.process_label not in calc_cls:
            raise OutputParsingError("{}: Unexpected calculation type to parse: {}".format(
                self.__class__.__name__,
                calc_node.__class__.__name__
            ))

        self.stdout_parser = None
        self.converged_ionic = None
        self.converged_electronic = None
        self._nodes = []
        super(CrystalParser, self).__init__(calc_node)

    # pylint: disable=protected-access
    def parse(self, retrieved_temporary_folder=None, **kwargs):
        """
        Parse outputs, store results in database.

        :param retrieved_temporary_folder: absolute path to the temporary folder on disk
        :returns: a tuple with two values ``(bool, node_list)``,
          where:

          * ``bool``: variable to tell if the parsing succeeded
          * ``node_list``: list of new nodes to be stored in the db
            (as a list of tuples ``(link_name, node)``)
        """
        success = False
        node_list = []

        # Check that the retrieved folder is there
        if retrieved_temporary_folder is None:
            self.logger.error("No retrieved folder found")
            return success, node_list

        # parameters should be parsed first, as the results
        with retrieved_temporary_folder.open(self.node.get_option('output_filename')) as f:
            self.add_node(self._linkname_parameters, f, self.parse_stdout)
        with retrieved_temporary_folder.open('fort.9', 'rb') as f:
            self.add_node(self._linkname_wavefunction, f, self.parse_out_wavefunction)
        with retrieved_temporary_folder.open('fort.34') as f:
            self.add_node(self._linkname_structure, f, self.parse_out_structure)
        with retrieved_temporary_folder.open(self.node.get_option('output_filename')) as f:
            self.add_node(self._linkname_trajectory, f, self.parse_out_trajectory)
        success = True
        return success, self._nodes

    def add_node(self, link_name, f, callback):
        """
        Add output nodes from parse functions
        :param link_name: output node link
        :param f: output file handle
        :param callback: callback function
        """
        parse_result = callback(f)
        if parse_result is not None:
            self._nodes.append((link_name, parse_result))

    def parse_stdout(self, f):
        self.stdout_parser = out.OutFileParser(f)
        params = self.stdout_parser.get_parameters()
        # raise flag if structure (atomic and electronic) is good
        self.converged_electronic = params['converged_electronic']
        self.converged_ionic = params['converged_ionic']
        return DataFactory('dict')(dict=params)

    def parse_out_structure(self, f):
        if not self.converged_ionic:
            return None
        parser = Fort34().read(f)
        return parser.to_aiida()

    def parse_out_wavefunction(self, f):
        if not self.converged_electronic:
            return None
        return DataFactory('singlefile')(file=f)

    def parse_out_trajectory(self, _):
        ase_structs = self.stdout_parser.get_trajectory()
        if not ase_structs:
            return None
        structs = [DataFactory('structure')(ase=struct) for struct in ase_structs]
        traj = DataFactory('array.trajectory')()
        traj.set_structurelist(structs)
        return traj
