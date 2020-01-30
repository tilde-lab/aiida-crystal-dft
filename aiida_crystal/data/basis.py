#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
The module describes basis set as the subclass of ParameterData
"""
import json

from pyparsing import ParseException
from ase.data import chemical_symbols

from aiida.orm import Dict
from aiida.common import UniquenessError
from aiida_crystal.io.parsers import gto_basis_parser
from aiida_crystal.utils.data import orbital_data


def md5(d, enc='utf-8'):
    """
    Returns MD5 hash of the dictionary (dumped to the string) in hex format
    :param d: dictionary
    :param enc: strung encoding
    :return: MD5 digest string
    """
    from hashlib import md5 as md5_func
    return md5_func(json.dumps(d).encode(enc)).hexdigest()


class CrystalBasisData(Dict):
    """
    a data type to store CRYSTAL basis sets in ParameterData format
    """

    @property
    def md5(self):
        """ md5 hash of the basis set """
        return self.get_attr('md5', default=None)

    @property
    def element(self):
        """ basis set element """
        return chemical_symbols[self.get_dict()['header'][0] - (0 if self.all_electron else 200)]

    @property
    def all_electron(self):
        return "ecp" not in self.get_dict()

    @property
    def content(self):
        basis = self.get_dict()
        s = ["{} {}".format(*basis['header']), ]
        if 'ecp' in basis:
            s.append(basis['ecp'][0])
            # INPUT ecp goes here
            if len(basis['ecp']) > 1:
                s.append('{} {} {} {} {} {} {}'.format(*basis['ecp'][1]))
                s += ['{} {} {}'.format(*x) for x in basis['ecp'][2]]
        for shell in basis['bs']:
            s.append('{} {} {} {} {}'.format(*shell[0]))
            if len(shell) > 1:
                # either 2 or 3 numbers represent each exponent
                exp = "   ".join(["{:.6f}"]*len(shell[1]))
                s += [exp.format(*x) for x in shell[1:]]
        return '\n'.join(s)

    @classmethod
    def from_md5(cls, checksum):
        """
        Return a list of all Basis Sets that match a given MD5 hash.

        Note that the hash has to be stored in a _md5 attribute, otherwise
        the basis will not be found.
        """
        from aiida.orm.querybuilder import QueryBuilder
        qb = QueryBuilder()
        qb.append(cls, filters={'attributes.md5': {'==': checksum}})
        return [_ for [_] in qb.all()]

    @classmethod
    def from_file(cls, file_name):
        """Reads in the basis from file and checks if the same basis is already present in the DB.
        Returns existing basis if present.

        :param file_name: The name of the file containing the basis
        :return: Class instance
        """
        with open(file_name, 'r') as f:
            try:
                basis = gto_basis_parser().parseString(f.read())
            except ParseException as ex:
                raise Exception("Parsing of {} failed: {} (at line:{}, col:{})".format(
                    file_name, ex.msg, ex.lineno, ex.col))
        md5_hash = md5(basis.asDict())
        bases = cls.from_md5(md5_hash)
        if bases:
            return bases[0]
        return cls(dict=basis.asDict()).store(use_cache=True)

    def set_oxistate(self, oxi_state, high_spin_preferred=False):
        """Set oxidation state for the basis"""
        # The algorithm is as follows:
        # 1. if oxi_state is positive (electrons are subtracted), then subtract electrons from valence orbital.
        # If two orbitals are valence, then subtract from the orbital with higher l
        # 2. if oxi_state is negative (electrons are added) and high spin is preferred, then add electrons to the
        # empty orbital with higher l than valence. If not (by default), then add electrons on valence orbital with the
        # highest l.

    def store(self, with_transaction=True, use_cache=None):
        # check if the dictionary has needed keys (may be it's incomplete?)
        if ("header" not in self.get_dict()) or ("bs" not in self.get_dict()):
            raise ValueError("Basis set for element {} does not contain required keys".format(self.element))
        md5_hash = md5(self.get_dict())
        if self.from_md5(md5_hash):
            raise UniquenessError("Basis with MD5 hash {} has already found in the database!".format(md5_hash))
        self.set_attribute("md5", md5_hash)
        return super(CrystalBasisData, self).store(with_transaction=with_transaction,
                                                   use_cache=use_cache)

    def _get_occupations(self):
        """
        A helper function providing a dictionary of orbital types and basis occupations
        :return: a dictionary of [orbital type, occupation] elements
        """
        occs = [[orb[0][1], orb[0][3]] for orb in self.get_dict()['bs']]
        result = {"s": [], "d": [], "f": []}
        if any([occ[0] == 1 for occ in occs]):
            result["sp"] = []
        else:
            result["p"] = []
        for orb, e in occs:
            result[orbital_data[orb]["l"]].append(e)
        return result
