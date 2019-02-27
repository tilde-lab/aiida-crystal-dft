#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida.parsers.parser import Parser
from aiida.parsers.exceptions import OutputParsingError
from aiida.orm import CalculationFactory
from aiida_crystal.io.f25 import Fort25


class PropertiesParser(Parser):
    """
    Parser class for parsing output of CRYSTAL calculation.
    """
    _linkname_bands = "output_bands"
    _linkname_dos = "output_dos"
    _calc_entry_points = ('crystal.properties', )

    # pylint: disable=protected-access
    def __init__(self, calculation):
        """
        Initialize Parser instance
        """
        super(PropertiesParser, self).__init__(calculation)

        calc_cls = [CalculationFactory(entry_point) for entry_point in self._calc_entry_points]

        # check for valid input
        if not isinstance(calculation, tuple(calc_cls)):
            raise OutputParsingError("{}: Unexpected calculation type to parse: {}".format(
                self.__class__.__name__,
                calculation.__class__.__name__
            ))

        self._nodes = []

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
        list_of_files = out_folder.get_content_list()
        output_files = self._calc.retrieve_list
        # Note: set(A) <= set(B) checks whether A is a subset
        if set(output_files) <= set(list_of_files):
            pass
        else:
            self.logger.error("Not all expected output files {} were found".
                              format(output_files))

        self.add_node(self._linkname_bands,
                      out_folder.get_abs_path("fort.25"),
                      self.parse_bands)
        success = True
        return success, self._nodes

    def add_node(self, link_name, file_name, callback):
        """Adds nodes to parser results"""
        try:
            self._nodes.append((link_name, callback(file_name)))
        except (ValueError, NotImplementedError) as err:
            self.logger.warning("Exception {} was raised while parsing {}".format(err, link_name))

    def parse_bands(self, file_name):
        """Parse bands from fort.25 file"""
        # from aiida.tools import get_kpoints_path, get_explicit_kpoints_path
        # from aiida.orm.data.array.kpoints import KpointsData
        # from aiida.orm.data.array.bands import BandsData
        parser = Fort25(file_name)
        result = parser.parse()
        bands = result["bands"]
        # to get BandsData node first we need to get k-points path and set KpointsData
        shrink = self._calc.inp.parameters.dict.band['shrink']
        path = bands["path"]
        if not bands:
            self.logger.info("Sorry, didn't find bands info in fort.25")

