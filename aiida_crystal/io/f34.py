#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

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
        self.atoms = None
        self.symops = None
        self.space_group = None

    def from_aiida(self):
        pass

    def from_ase(self, ase_struct):
        if all(ase_struct.pbc):
            self.dimensionality = 3
        else:
            raise NotImplemented('Structure with dimensionality < 3 currently not supported')
        cell = (ase_struct.get_cell(), ase_struct.get_scaled_positions(), ase_struct.get_atomic_numbers())
        dataset = spglib.get_symmetry_dataset(cell)
        self.space_group = dataset['number']
        self.crystal_type = get_crystal_system(self.space_group, as_number=True)
        self.centring = get_centering_code(self.space_group, dataset['international'])
        return self

    def read(self, file_name):
        pass

    def write(self, file_name):
        pass
