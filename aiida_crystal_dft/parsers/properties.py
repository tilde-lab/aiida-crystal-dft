#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import numpy as np
from aiida.parsers.parser import Parser
from aiida.common import OutputParsingError, NotExistent
from aiida.plugins import CalculationFactory
from aiida_crystal_dft.io.f25 import Fort25
from aiida_crystal_dft.io.f9 import Fort9
from aiida_crystal_dft.utils.kpoints import construct_kpoints_path, get_explicit_kpoints_path


class PropertiesParser(Parser):
    """
    Parser class for parsing output of CRYSTAL calculation.
    """
    _linkname_bands = "output_bands"
    _linkname_dos = "output_dos"

    # pylint: disable=protected-access
    def __init__(self, calc_node):
        """
        Initialize Parser instance
        """
        calc_entry_points = ('crystal_dft.properties',)

        calc_cls = [CalculationFactory(entry_point).get_name() for entry_point in calc_entry_points]
        if calc_node.process_label not in calc_cls:
            raise OutputParsingError("{}: Unexpected calculation type to parse: {}".format(
                self.__class__.__name__,
                calc_node.__class__.__name__
            ))

        self._nodes = []
        super(PropertiesParser, self).__init__(calc_node)

    # pylint: disable=protected-access
    def parse(self, retrieved_temporary_folder=None, **kwargs):
        """
        Parse outputs, store results in database.

        :param retrieved_temporary_folder: a FolderData returned from the calculation
        :returns: a tuple with two values ``(bool, node_list)``,
          where:

          * ``bool``: variable to tell if the parsing succeeded
          * ``node_list``: list of new nodes to be stored in the db
            (as a list of tuples ``(link_name, node)``)
        """
        # Check that the retrieved folder is there
        try:
            folder = self.retrieved
        except NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        # parse file here
        with folder.open("fort.25") as f:
            parser = Fort25(f)
            result = parser.parse()
            self.add_node(self._linkname_bands,
                          result.get("BAND", None),
                          self.parse_bands)
            self.add_node(self._linkname_dos,
                          result.get("DOSS", None),
                          self.parse_dos)

    def add_node(self, link_name, file_name, callback):
        """Adds nodes to parser results"""
        try:
            self.out(link_name, callback(file_name))
        except (ValueError, NotImplementedError) as err:
            self.logger.warning("Exception {} was raised while parsing {}".format(err, link_name))

    def parse_bands(self, bands):
        """Parse bands from fort.25 file"""
        if not bands:
            raise ValueError("Sorry, didn't find bands info in fort.25")

        from aiida.plugins import DataFactory
        # to get BandsData node first we need to get k-points path and set KpointsData
        shrink = self.node.inputs.parameters.dict.band['shrink']
        path = bands["path"]
        k_number = bands["n_k"]
        # for path construction we're getting geometry from fort.9
        with self.node.inputs.wavefunction.open() as f:
            fort9_name = f.name
        geometry_parser = Fort9(fort9_name)
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
