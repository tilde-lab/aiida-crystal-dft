#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import numpy as np
from aiida.parsers.parser import Parser
from aiida.common import OutputParsingError
from aiida.plugins import CalculationFactory
from aiida_crystal.io.f25 import Fort25
from aiida_crystal.io.f9 import Fort9
from aiida_crystal.utils.kpoints import construct_kpoints_path, get_explicit_kpoints_path


class PropertiesParser(Parser):
    """
    Parser class for parsing output of CRYSTAL calculation.
    """
    _linkname_bands = "output_bands"
    _linkname_dos = "output_dos"
    _linkname_input_parameters = "input_parameters"
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
        list_of_files = out_folder.get_folder_list()
        output_files = self._calc.retrieve_list
        # Note: set(A) <= set(B) checks whether A is a subset
        if set(output_files) <= set(list_of_files):
            pass
        else:
            self.logger.error("Not all expected output files {} were found".
                              format(output_files))

        # parse file here
        parser = Fort25(out_folder.get_abs_path("fort.25"))
        result = parser.parse()
        self.add_node(self._linkname_bands,
                      result.get("BAND", None),
                      self.parse_bands)
        self.add_node(self._linkname_dos,
                      result.get("DOSS", None),
                      self.parse_dos)

        success = True
        return success, self._nodes

    def add_node(self, link_name, file_name, callback):
        """Adds nodes to parser results"""
        try:
            self._nodes.append((link_name, callback(file_name)))
        except (ValueError, NotImplementedError) as err:
            self.logger.warning("Exception {} was raised while parsing {}".format(err, link_name))

    def parse_bands(self, bands):
        """Parse bands from fort.25 file"""
        if not bands:
            raise ValueError("Sorry, didn't find bands info in fort.25")

        from aiida.plugins import DataFactory
        # to get BandsData node first we need to get k-points path and set KpointsData
        shrink = self._calc.inp.parameters.dict.band['shrink']
        path = bands["path"]
        k_number = bands["n_k"]
        # for path construction we're getting geometry from fort.9
        geometry_parser = Fort9(self._calc.inp.wavefunction.get_file_abs_path())
        cell = geometry_parser.get_cell(scale=True)
        path_description = construct_kpoints_path(cell, path, shrink, k_number)
        structure = DataFactory('structure')(ase=geometry_parser.get_ase())
        # and now find k-points along the path
        k_points = get_explicit_kpoints_path(structure, path_description)['explicit_kpoints']
        # ...and finally populate bands data
        bands_data = DataFactory('array.bands')()
        bands_data.set_kpointsdata(k_points)
        bands_data.set_bands(bands["bands"])
        return bands_data

    def parse_dos(self, data):
        """A function that returns ArrayData with densities of states. The array should have shape (nproj+2, ne),
        where ne is the number of energy points, and nproj is the number of DOS projections"""
        if not data:
            raise ValueError("Sorry, didn't find dos info in fort.25")

        from aiida.plugins import DataFactory
        array_data = DataFactory("array")()
        array_data.set_array("dos", np.vstack((data["e"], data["dos"])))
        return array_data
