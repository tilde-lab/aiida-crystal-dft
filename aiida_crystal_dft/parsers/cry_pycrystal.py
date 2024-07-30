# -*- coding: utf-8 -*-
"""
Pycrystal-based parser for CRYSTAL AiiDA plugin
"""
from aiida.parsers.parser import Parser
from aiida.common import OutputParsingError, NotExistent
from aiida.plugins import CalculationFactory, DataFactory

from aiida_crystal_dft.io.pycrystal import out
from aiida_crystal_dft.io.f34 import Fort34


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
        calc_entry_points = ['crystal_dft.serial',
                             'crystal_dft.parallel'
                             ]
        calc_cls = {CalculationFactory(entry_point).get_name(): entry_point for entry_point in calc_entry_points}
        if calc_node.process_label not in calc_cls:
            raise OutputParsingError("{}: Unexpected calculation type to parse: {}".format(
                self.__class__.__name__,
                calc_node.__class__.__name__
            ))

        self.is_parallel = "parallel" in calc_cls[calc_node.process_label]
        self.stdout_parser = None
        self.converged_ionic = None
        self.converged_electronic = None

        super(CrystalParser, self).__init__(calc_node)

    # pylint: disable=protected-access
    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.
        """

        # Check that the retrieved folder is there
        try:
            folder = self.retrieved
        except NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        # parameters should be parsed first, as the results
        if self.is_parallel:
            results_file = self._node.get_option('scheduler_stderr')
        else:
            results_file = self._node.get_option('output_filename')

        # Check if we can parse results file, the error message if not
        try:
            with folder.open(results_file) as f:
                print(out.OutFileParser(f).get_parameters())
        except out.CRYSTOUT_Error as ex:
            if 'Inadequate elastic calculation' in ex.msg:
                return self.exit_codes.ERROR_REOPTIMIZATION_NEEDED
        # TODO: refactor this later
        # Check for error file contents
        scf_failed = False
        if 'fort.87' in folder.list_object_names():
            with folder.open('fort.87') as f:
                error = f.readline()

                # check for scf failed, remember it and parse as much as we can
                if 'SCF FAILED' in error or 'TOO MANY ITERATIONS' in error:
                    scf_failed = True

                elif 'UNIT CELL NOT NEUTRAL' in error:
                    return self.exit_codes.ERROR_UNIT_CELL_NOT_NEUTRAL

                elif 'BASIS SET LINEARLY DEPENDENT' in error:
                    return self.exit_codes.ERROR_BASIS_SET_LINEARLY_DEPENDENT

                elif 'NEIGHBOR LIST TOO BIG' in error:
                    return self.exit_codes.ERROR_NEIGHBOR_LIST_TOO_BIG

                elif 'GEOMETRY OPTIMIZATION FAILED' in error:
                    return self.exit_codes.ERROR_GEOMETRY_OPTIMIZATION_FAILED

                elif 'ALL G-VECTORS USED' in error:
                    return self.exit_codes.ERROR_NO_G_VECTORS

                elif 'SMALLDIST' in error:
                    return self.exit_codes.ERROR_GEOMETRY_COLLAPSED

                elif 'PARAMETERS FOR MODEL HESSIAN NOT DEFINED' in error:
                    return self.exit_codes.ERROR_HESSIAN_PARAMETERS_NOT_DEFINED

                elif 'FERMI ENERGY NOT IN INTERVAL' in error:
                    return self.exit_codes.ERROR_FERMI_ENERGY

                elif 'RECIPROCAL' in error:
                    return self.exit_codes.ERROR_MADELUNG_SUMS

                elif 'ALLOCATION' in error:
                    return self.exit_codes.ERROR_ALLOCATION

                elif 'CLOSED SHELL RUN-SPIN POLARIZATION NOT ALLOWED' in error:
                    return self.exit_codes.ERROR_CLOSED_SHELL_SPIN

                elif error:
                    return self.exit_codes.ERROR_UNKNOWN

        with folder.open(results_file) as f:
            self.add_node(self._linkname_parameters, f, self.parse_stdout)
        with folder.open('fort.9', 'rb') as f:
            self.add_node(self._linkname_wavefunction, f, self.parse_out_wavefunction)
        with folder.open('fort.34') as f:
            self.add_node(self._linkname_structure, f, self.parse_out_structure)
        with folder.open(results_file) as f:
            self.add_node(self._linkname_trajectory, f, self.parse_out_trajectory)
        if scf_failed:
            return self.exit_codes.ERROR_SCF_FAILED
        return None

    def add_node(self, link_name, f, callback):
        """
        Add output nodes from parse functions
        :param link_name: output node link
        :param f: output file handle
        :param callback: callback function
        """
        parse_result = callback(f)
        if parse_result is not None:
            self.out(link_name, parse_result)

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
        try:
            ase_structs = self.stdout_parser.get_trajectory()
            if not ase_structs:
                return None
            structs = [DataFactory('structure')(ase=struct) for struct in ase_structs]
            traj = DataFactory('array.trajectory')()
            traj.set_structurelist(structs)
            return traj
        except ValueError as e:
            # Fix for calculation with SCELPHO keyword;
            # Scince supercell have more atoms than regular cell;
            # traj.set_structurelist(structs) will throw an error https://github.com/aiidateam/aiida-core/blob/71422eb872040a9ba23047d2ec031f6deaa6a7cc/src/aiida/orm/nodes/data/array/trajectory.py#L202 
            # There are no reason for tracking trajectory in phonon calculation, so it will return None
            if "Phonon" in self._node.label:
                self._logger.warning(f"Caught ValueError for node with label '{self._node.label}': {e}")
                return None
            else:
                raise e
