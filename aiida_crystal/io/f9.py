#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""A parser for fort.9, the binary file with wave functions
"""
import os
from scipy.io import FortranFile
from ase import Atoms
from aiida_crystal.utils.geometry import cart2frac


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
        self._name = file_name
        self._geometry = None

    def _read_geometry(self):
        """Returns geometry from fort.9. All lengths are in Bohr. If scale=True, then convert positions to fractional.
        If ase=True, returns geometry as ase Atoms (independently of scale)"""
        # read arrays from file
        with FortranFile(self._name) as f:
            data = [f.read_record(rtype) for rtype in self._record_types]
        # the first 9 entries of the 5th record (if counting from 0) contain cell
        cell = data[5][:9].reshape(3, 3)
        # the 7th record contains atomic numbers
        numbers = data[7].astype(int)
        # the 8th record contains cartesian atomic coordinates
        positions = data[8].reshape(len(numbers), 3)
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

    def get_ase(self):
        """Returns ase Atoms object"""
        if self._geometry is None:
            self._read_geometry()
        cell, positions, numbers = self._geometry
        return Atoms(cell=cell, positions=positions, numbers=numbers, pbc=True)

    def get_structure(self):
        """Returns aiida StructureData"""
        from aiida.orm import DataFactory
        return DataFactory('structure')(ase=self.get_ase())
