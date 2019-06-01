#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
The module describes basis set as the subclass of ParameterData
"""

from aiida.orm.data.parameter import ParameterData
from aiida_crystal.io.parsers import gto_basis_parser


class CrystalBasisData(ParameterData):
    """
    a data type to store CRYSTAL basis sets in ParameterData format
    """

    @property
    def md5sum(self):
        """ return the md5 hash of the basis set

        :return:
        """
        return self.get_attr('md5', None)

    @classmethod
    def from_md5(cls, md5):
        """
        Return a list of all Basis Sets that match a given MD5 hash.

        Note that the hash has to be stored in a _md5 attribute, otherwise
        the basis will not be found.
        """
        from aiida.orm.querybuilder import QueryBuilder
        qb = QueryBuilder()
        qb.append(cls, filters={'attributes.md5': {'==': md5}})
        return [_ for [_] in qb.all()]

