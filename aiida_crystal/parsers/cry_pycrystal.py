# -*- coding: utf-8 -*-
"""
Pycrystal-based parser for CRYSTAL AiiDA plugin
"""

from __future__ import absolute_import

from aiida.parsers.parser import Parser
from aiida.parsers.exceptions import OutputParsingError
from aiida.orm import CalculationFactory
from aiida.orm.data.parameter import ParameterData
from aiida.orm.data.structure import StructureData
from aiida.orm.data.singlefile import SinglefileData
from aiida_crystal.io.pycrystal import out


class CrystalParser(Parser):
    """
    Parser class for parsing output of CRYSTAL calculation.
    """

    # pylint: disable=protected-access
    def __init__(self, calculation):
        """
        Initialize Parser instance
        """
        super(CrystalParser, self).__init__(calculation)
        calc_entry_points = ['crystal.basic',
                             'crystal.main',
                             ]

        calc_cls = [CalculationFactory(entry_point) for entry_point in calc_entry_points]

        # check for valid input
        if not isinstance(calculation, tuple(calc_cls)):
            raise OutputParsingError("{}: Unexpected calculation type to parse: {}".format(
                self.__class__.__name__,
                calculation.__class__.__name__
            ))
        # each parse_* function should return a list of [(link, node)...] format
        self._parse = {calculation._DEFAULT_OUTPUT_FILE: self.parse_stdout,
                       calculation._DEFAULT_EXTERNAL_FILE: self.parse_out_structure,
                       'fort.9': self.parse_out_wavefunction}

    # pylint: disable=protected-access
    def parse_with_retrieved(self, retrieved):
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
        list_of_files = out_folder.get_folder_list()
        output_files = self._calc.retrieve_list
        # Note: set(A) <= set(B) checks whether A is a subset
        if set(output_files) <= set(list_of_files):
            pass
        else:
            self.logger.error("Not all expected output files {} were found".
                              format(output_files))

        for fname in output_files:
            if fname in self._parse:
                node = self._parse[fname](out_folder.get_abs_path(fname))
                if isinstance(node, tuple):
                    node_list.append(node)
                else:
                    node_list += node
            else:
                self.logger.warning("Could not find a parser for {}".
                                    format(fname))

        success = True
        return success, node_list

    @classmethod
    def parse_stdout(cls, file_name):
        result = out.parse(file_name)

        return 'output_parameters', ParameterData(dict=result)

    @classmethod
    def parse_out_structure(cls, file_name):
        return []

    @classmethod
    def parse_out_wavefunction(cls, file_name):
        return 'wavefunction', SinglefileData(file=file_name)
