#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import numpy as np
import spglib

from ase import Atoms
from ase.data import chemical_symbols

import pyparsing as pp
from aiida_crystal.utils.geometry import get_crystal_system, get_centering_code
from aiida_crystal.io import _parse_string
from aiida_crystal.io.basis import BasisAdapter

PC = pp.pyparsing_common


def f34_parser():
    """Fort.34 pyparsing parser"""
    header = (3 * PC.integer).setResultsName('header')
    cell = (9 * PC.sci_real).setResultsName('abc')
    nsymops = PC.integer.setResultsName('n_symops')
    symops = pp.OneOrMore(PC.sci_real).setResultsName('symops')
    nat = PC.integer.setResultsName('nat')
    geom = pp.OneOrMore(pp.Group(PC.integer + 3 * PC.sci_real)).setResultsName('geometry')
    return header + pp.Suppress(pp.restOfLine) + cell + nsymops + symops + nat + geom


class Fort34(object):

    def __init__(self, basis=None):
        """
        A reader and writer of fort.34 (or instruct.gui) CRYSTAL input/output file.
        Stores geometry internally as conventional cell; rotations are stored for primitive cell (otherwise we can not
        get symmetry number properly).
        converts to primitive before writing the file
        """
        self.dimensionality = None
        self.centring = None
        self.crystal_type = None
        self.positions = None
        self.n_symops = 0
        self.symops = None
        self.space_group = None
        self.abc = None
        self.atomic_numbers = None
        self.basis = None

        # a BasisFamily instance or a list of bases
        if basis:
            self.basis = BasisAdapter(basis)

    def from_aiida(self, aiida_struct):
        """
        Convert aiida StructureData to format suitable for writing fort.34 file
        :param aiida_struct: aiida StructureData object
        :return: a Fort34 instance
        """
        ase_struct = aiida_struct.get_ase()
        return self.from_ase(ase_struct)

    def from_ase(self, ase_struct):
        """
        Convert ase Atoms to format suitable for writing fort.34 file
        :param ase_struct: ase Atoms object
        :return: a Fort34 instance
        """
        if all(ase_struct.pbc):
            self.dimensionality = 3
        else:
            raise NotImplementedError('Structure with dimensionality < 3 currently not supported')

        abc = ase_struct.get_cell()
        positions = ase_struct.get_scaled_positions()
        atomic_numbers = ase_struct.get_atomic_numbers()
        cell = (abc, positions, atomic_numbers)

        # get conventional cell
        cell = spglib.standardize_cell(cell, to_primitive=False, no_idealize=False)
        self.abc, self.positions, self.atomic_numbers = cell

        # symmetries related stuff
        dataset = spglib.get_symmetry_dataset(spglib.find_primitive(cell))
        self.space_group = dataset['number']
        self.crystal_type = get_crystal_system(self.space_group, as_number=True)
        self.centring = get_centering_code(self.space_group, dataset['international'])
        self.n_symops = len(dataset["translations"])
        self.symops = np.zeros((self.n_symops * 4, 3), dtype=float)

        # convert symmetry operations from fractional to cartesian
        rotations = np.dot(self.abc.T, np.dot(dataset["rotations"], np.linalg.inv(self.abc.T)))
        rotations = np.swapaxes(rotations, 0, 1)
        translations = np.dot(dataset["translations"], self.abc)
        self.symops[0::4] = rotations[:, 0]
        self.symops[1::4] = rotations[:, 1]
        self.symops[2::4] = rotations[:, 2]
        self.symops[3::4] = translations
        return self

    def to_ase(self):
        """Return conventional unit cell in ase format"""
        # cell here should be conventional!
        return Atoms(symbols=[chemical_symbols[n] for n in self.atomic_numbers],
                     scaled_positions=self.positions,
                     cell=self.abc,
                     pbc=True)

    def to_aiida(self):
        """Return structure in aiida format"""
        from aiida.plugins import DataFactory
        return DataFactory('structure')(ase=self.to_ase())

    def read(self, file):
        """Read and parse fort.34 file"""
        if isinstance(file, str):
            with open(file) as f:
                data = f.read()
        else:
            data = file.read()
        parsed_data = _parse_string(f34_parser(), data)
        self.dimensionality, self.centring, self.crystal_type = parsed_data['header']
        if self.dimensionality != 3:
            raise NotImplementedError('Structure with dimensionality < 3 currently not supported')

        # primitive cell vectors and basis positions in cartesian coordinates
        abc = np.array(parsed_data['abc'].asList()).reshape((3, 3))
        positions = np.array([d[1:] for d in parsed_data['geometry']])

        # convert positions to fractional
        positions = np.dot(np.linalg.inv(abc).T, positions.T).T
        atomic_numbers = [d[0] for d in parsed_data['geometry']]

        # convert to conventional cell
        cell = (abc, positions, atomic_numbers)
        cell = spglib.standardize_cell(cell, to_primitive=False, no_idealize=False)
        self.abc, self.positions, atomic_numbers = cell

        # ECPs
        self.atomic_numbers = [num if num < 201 else num - 200 for num in atomic_numbers]

        # get symmetry operations
        self.n_symops = parsed_data['n_symops']
        self.symops = np.array(parsed_data['symops'].asList()).reshape(self.n_symops * 4, 3)
        rotations = np.zeros((self.n_symops, 3, 3))
        for i in range(3):
            rotations[:, i] = self.symops[i::4]

        # convert symmetry operations from cartesian to fractional
        rotations = np.dot(np.dot(np.linalg.inv(abc.T), rotations), abc.T)

        # have to round rotations matrix as it is used to find symmetry group
        rotations = np.round(np.swapaxes(rotations, 0, 1), 9)
        translations = np.dot(self.symops[3::4], np.linalg.inv(abc))
        hall = spglib.get_hall_number_from_symmetry(rotations, translations)
        self.space_group = int(spglib.get_spacegroup_type(hall)['number'])
        return self

    def __str__(self):
        # check for ECPs in basis family
        has_ecp = []
        if self.basis and not self.basis.predefined:
            composition = set(self.atomic_numbers)
            has_ecp = [num for num in composition if not self.basis.get_basis(chemical_symbols[num]).all_electron]

        # convert geometry to primitive and find inequivalent atoms
        cell = self.abc, self.positions, self.atomic_numbers
        cell = spglib.standardize_cell(cell, to_primitive=True, no_idealize=False)
        abc, positions, atomic_numbers = cell

        # symmetries related stuff
        dataset = spglib.get_symmetry_dataset(cell)

        # leave only symmetrically inequivalent atoms
        inequiv_atoms = np.unique(dataset['equivalent_atoms'])
        positions = positions[inequiv_atoms]
        atomic_numbers = atomic_numbers[inequiv_atoms]

        # convert positions from fractional to cartesian
        positions = np.dot(abc.T, positions.T).T

        # convert symmetry operations from fractional to cartesian
        rotations = np.dot(abc.T, np.dot(dataset["rotations"], np.linalg.inv(abc.T)))
        rotations = np.swapaxes(rotations, 0, 1)
        translations = np.dot(dataset["translations"], abc)
        n_symops = len(dataset["translations"])
        symops = np.zeros((n_symops * 4, 3), dtype=float)
        symops[0::4] = rotations[:, 0]
        symops[1::4] = rotations[:, 1]
        symops[2::4] = rotations[:, 2]
        symops[3::4] = translations

        # make a list of lines
        f34_lines = ["{0} {1} {2}".format(self.dimensionality,
                                          self.centring,
                                          self.crystal_type)]
        f34_lines += ["{0[0]:17.9E} {0[1]:17.9E} {0[2]:17.9E}".format(
            np.round(vec, 9) + 0.) for vec in abc]

        # symmetry operation part
        f34_lines.append(str(n_symops))
        f34_lines += ["{0[0]:17.9E} {0[1]:17.9E} {0[2]:17.9E}".format(
            np.round(line, 9) + 0.) for line in symops]
        # atoms part
        f34_lines.append(str(len(atomic_numbers)))
        f34_lines += ["{0:3} {1[0]:17.9E} {1[1]:17.9E} {1[2]:17.9E}".format(
            anum + 200 if anum in has_ecp else anum, pos) for anum, pos in zip(atomic_numbers, positions)]

        return "\n".join(f34_lines)

    def write(self, f):
        """Write geometry to file fort.34"""
        print(self, file=f)
