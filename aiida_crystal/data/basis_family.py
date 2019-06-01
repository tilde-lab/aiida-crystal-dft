#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
A module describing the CRYSTAL basis family (Str on steroids)
"""

from aiida.orm.data.str import Str

BASIS_FAMILY_KWDS = [
    "STO-3G",
    "STO-6G",
    "POB-DZVP",
    "POB-DZVPP",
    "POB-TZVP"
]


class CrystalBasisFamilyData(Str):

    def __init__(self, *args, **kwds):
        super(CrystalBasisFamilyData, self).__init__(*args, **kwds)

    @classmethod
    def _get(cls, name):
        # check if we can find the basis family
        from aiida.orm.querybuilder import QueryBuilder
        qb = QueryBuilder()
        qb.append(cls)
        for res in qb.all():
            if res[0].get_attr('value') == name:
                return res[0]
        return None

    @classmethod
    def get_or_create(cls, name, basis_sets=None):
        """
        The class method gets the basis family or creates it if it's not existent
        :param name: basis family name
        :param basis_sets: an iterable of basis sets to add to group
        :return: the CrystalBasisFamilyData instance
        """
        found = cls._get(name)
        if found:
            return found
        # creating basis family
        if name in BASIS_FAMILY_KWDS:
            if basis_sets is not None:
                raise ValueError("{} is a predefined basis family in CRYSTAL; can't add basis sets to it".format(name))
            # return the instance
            return cls(name)
        return NotImplementedError

    def content(self):
        """Content for adding to .d12
        """
        if self.value in BASIS_FAMILY_KWDS:
            return "BASISSET\n{}\n".format(self.value)
        else:
            raise NotImplementedError
