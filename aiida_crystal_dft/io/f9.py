#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""A parser for fort.9, the binary file with wave functions
"""
import os
from scipy.io import FortranFile
from ase import Atoms
from aiida_crystal_dft.utils.geometry import cart2frac


class Fort9(object):

    # limXXX, par, tol, inf, ?, xyvgve, ninv, basato(Z, crd), ...
    _record_types = ("int32", "float64", "int32", "int32", "float64", "float64", "int32", "float64", "float64")

    def __init__(self, file_name):
        """
        The parser for unformatted fort.9 file. For now just finds geometry.

        :param file_name: fort.9 file name
        """
        # do our best to check if the file is fort.9
        if os.path.basename(file_name) != "fort.9":
            raise ValueError("Expected fort.9 as the file name, got {} instead".format(os.path.basename(file_name)))
        self._geometry = None
        # read arrays from file
        try:
            with FortranFile(file_name) as f:
                self._data = [f.read_record(rtype) for rtype in self._record_types]
        except TypeError:
            raise FileNotFoundError("Something is wrong with {} file, please check".format(file_name))

    def _read_geometry(self):
        """Returns geometry from fort.9. All lengths are in Bohr. If scale=True, then convert positions to fractional.
        If ase=True, returns geometry as ase Atoms (independently of scale)"""
        # the first 9 entries of the 5th record (if counting from 0) contain cell
        cell = self._data[5][:9].reshape(3, 3)
        # the 7th record contains atomic numbers
        numbers = self._data[7].astype(int)
        # the 8th record contains cartesian atomic coordinates
        positions = self._data[8].reshape(len(numbers), 3)
        # internally store positions in Cartesian coordinates
        self._geometry = (cell, positions, numbers)

    def get_cell(self, scale=True):
        """Returns cell in spglib sense. If scale=True, then converts cartesian coordinates to fractional"""
        if self._geometry is None:
            self._read_geometry()
        if not scale:
            return self._geometry
        cell, positions, numbers = self._geometry
        return cell, cart2frac(positions, cell), numbers

    def get_atomic_numbers(self):
        """Returns a list of atomic numbers in geometry order"""
        _, _, numbers = self.get_cell()
        return numbers

    def get_ase(self):
        """Returns ase Atoms object"""
        if self._geometry is None:
            self._read_geometry()
        cell, positions, numbers = self._geometry
        return Atoms(cell=cell, positions=positions, numbers=numbers, pbc=True)

    def get_structure(self):
        """Returns aiida StructureData"""
        from aiida.plugins import DataFactory
        return DataFactory('structure')(ase=self.get_ase())

    def get_ao_number(self):
        """Get number of atomic orbitals (which is the number of bands)"""
        # cast to python type for validation purposes
        return int(self._data[3][6])
