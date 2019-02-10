#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import numpy as np
import spglib
from .geometry import get_crystal_system, get_centering_code


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
            raise NotImplemented('Structure with dimensionality < 3 currently not supported')
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

    def read(self, file_name):
        raise NotImplemented

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
        print(self, file=f)
