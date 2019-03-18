#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from __future__ import print_function
import numpy as np
import spglib
from ase.spacegroup import crystal
from ase.data import chemical_symbols
import pyparsing as pp
from aiida_crystal.utils.geometry import get_crystal_system, get_centering_code
from aiida_crystal.io import _parse_string

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

    def __init__(self):
        """
        A reader and writer of fort.34 (or instruct.gui) CRYSTAL input?output file
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

        cell = spglib.find_primitive(cell)
        self.abc, positions, self.atomic_numbers = cell
        # convert positions from fractional to cartesian
        self.positions = np.dot(self.abc, positions.T).T
        # symmetries related stuff
        dataset = spglib.get_symmetry_dataset(cell)
        self.space_group = dataset['number']
        self.crystal_type = get_crystal_system(self.space_group, as_number=True)
        self.centring = get_centering_code(self.space_group, dataset['international'])
        self.n_symops = len(dataset["translations"])
        self.symops = np.zeros((self.n_symops * 4, 3), dtype=int)
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
        return crystal(symbols=[chemical_symbols[n] for n in self.atomic_numbers],
                       basis=self.positions,
                       spacegroup=self.space_group,
                       cell=self.abc)

    def to_aiida(self):
        """Return structure in aiida format"""
        from aiida.orm import DataFactory
        return DataFactory('structure')(ase=self.to_ase())

    def read(self, file_name):
        """Read and parse fort.34 file"""
        with open(file_name) as f:
            data = f.read()
        parsed_data = _parse_string(f34_parser(), data)
        self.dimensionality, self.centring, self.crystal_type = parsed_data['header']
        if self.dimensionality != 3:
            raise NotImplementedError('Structure with dimensionality < 3 currently not supported')
        self.abc = np.array(parsed_data['abc'].asList()).reshape((3, 3))
        self.n_symops = parsed_data['n_symops']
        self.symops = np.array(parsed_data['symops'].asList()).reshape(self.n_symops * 4, 3)
        self.atomic_numbers = [d[0] for d in parsed_data['geometry']]
        self.positions = [d[1:] for d in parsed_data['geometry']]
        rotations = np.zeros((self.n_symops, 3, 3))
        for i in range(3):
            rotations[:, i] = self.symops[i::4]
        # convert symmetry operations from cartesian to fractional
        rotations = np.dot(np.dot(np.linalg.inv(self.abc.T), rotations), self.abc.T)
        # have to round rotations matrix as it is used to find symmetry group
        rotations = np.round(np.swapaxes(rotations, 0, 1), 9)
        translations = np.dot(self.symops[3::4], np.linalg.inv(self.abc))
        hall = spglib.get_hall_number_from_symmetry(rotations, translations)
        self.space_group = spglib.get_spacegroup_type(hall)['number']
        return self

    def __str__(self):
        f34_lines = ["{0} {1} {2}".format(self.dimensionality,
                                          self.centring,
                                          self.crystal_type)]
        f34_lines += ["{0[0]:17.9E} {0[1]:17.9E} {0[2]:17.9E}".format(
            np.round(vec, 9) + 0.) for vec in self.abc]
        # symmetry operation part
        f34_lines.append(str(self.n_symops))
        f34_lines += ["{0[0]:17.9E} {0[1]:17.9E} {0[2]:17.9E}".format(
            np.round(line, 9) + 0.) for line in self.symops]
        # atoms part
        f34_lines.append(str(len(self.atomic_numbers)))
        f34_lines += ["{0:3} {1[0]:17.9E} {1[1]:17.9E} {1[2]:17.9E}".format(anum, pos)
                      for anum, pos in zip(self.atomic_numbers, self.positions)]

        return "\n".join(f34_lines)

    def write(self, f):
        """Write geometry to file fort.34"""
        print(self, file=f)
