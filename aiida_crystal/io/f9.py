#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""A parser for fort.9, the binary file with wave functions
"""
import os
from scipy.io import FortranFile
from aiida_crystal.utils.geometry import cart2frac


def _open(file_name):
    """Opens fort.9 as a Fortran file"""
    return FortranFile(file_name, "r")


class Fort9(object):

    # limXXX, par, tol, inf, ?, xyvgve, ninv, basato(Z, crd), ...
    _record_types = ("int32", "float64", "int32", "int32", "float64", "float64", "int32", "float64", "float64")

    def __init__(self, file_name):
        # do our best to check if the file is fort.9
        if os.path.basename(file_name) != "fort.9":
            raise ValueError("Expected fort.9 as the file name, got {} instead".format(os.path.basename(file_name)))
        self._name = file_name

    def get_geometry(self, scale=True):
        """Returns geometry from fort.9. All lengths are in Bohr. If scale=True, then convert positions to fractional"""
        f = _open(self._name)
        # read arrays from file
        data = [f.read_record(rtype) for rtype in self._record_types]
        # the first 9 entries of the 5th record (if counting from 0) contain cell
        cell = data[5][:9].reshape(3, 3)
        # the 7th record contains atomic numbers
        numbers = data[7].astype(int)
        # the 8th record contains cartesian atomic coordinates
        positions = data[8].reshape(len(numbers), 3)
        if scale:
            positions = cart2frac(positions, cell)
        return cell, positions, numbers
