#  Copyright (c)  Andrey Sobolev, 2019-20. Distributed under MIT license, see LICENSE file.

"""
The module describes basis set as the subclass of ParameterData
"""
import json

from pyparsing import ParseException
from ase.data import chemical_symbols

from aiida.orm import Dict
from aiida.common import UniquenessError
from aiida_crystal_dft.io.parsers import gto_basis_parser
from aiida_crystal_dft.utils.electrons import orbital_data, max_e, get_valence_shell


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
        return self.get_attribute('md5', default=None)

    @property
    def element(self):
        """ basis set element """
        return chemical_symbols[self.get_dict()['header'][0] - (0 if self.all_electron else 200)]

    @property
    def all_electron(self):
        return "ecp" not in self.get_dict()

    def content(self, oxi_state=0, high_spin_preferred=False):
        basis = self.set_oxistate(oxi_state, high_spin_preferred)
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
        return cls(dict=basis.asDict()).store()

    def set_oxistate(self, oxi_state, high_spin_preferred=False):
        """Set oxidation state for the basis"""
        # The algorithm is as follows:
        # 1. if oxi_state is positive (electrons are subtracted), then subtract electrons from valence orbital.
        # If two orbitals are valence, then subtract from sp orbital first, and then from the higher l orbital
        # 2. if oxi_state is negative (electrons are added) and high spin is preferred, then add electrons to the
        # empty orbital with higher l than valence. If not (by default), then add electrons on valence orbital with the
        # highest l.
        occs = self._get_occupations()
        # change oxidation state according to the algorithm above
        if oxi_state > 0:
            occs = remove_valence_electrons(oxi_state, occs, self.element)
        elif oxi_state < 0:
            occs = add_valence_electrons(-oxi_state, occs, self.element, high_spin_preferred)
        # alter basis dict and return it
        basis_dict = self.get_dict()
        for orb, occ in occs.items():
            if occ:
                orb_idx = [i for i, o in enumerate(basis_dict["bs"]) if orbital_data[o[0][1]]["l"] == orb]
                for i, o in zip(orb_idx, occ):
                    basis_dict["bs"][i][0][3] = o
        return basis_dict

    def store(self, with_transaction=True, use_cache=None):
        # check if the dictionary has needed keys (may be it's incomplete?)
        if ("header" not in self.get_dict()) or ("bs" not in self.get_dict()):
            raise ValueError("Basis set for element {} does not contain required keys".format(self.element))
        md5_hash = md5(self.get_dict())
        if self.from_md5(md5_hash):
            raise UniquenessError("Basis with MD5 hash {} has already found in the database!".format(md5_hash))
        self.set_attribute("md5", md5_hash)
        return super(CrystalBasisData, self).store(with_transaction=with_transaction)

    def _get_occupations(self):
        """A wrapper for get_occupations function"""
        return get_occupations(self.get_dict())


def get_occupations(basis_dict):
    """A helper function providing a dictionary of orbital types and basis occupations, given basis dictionary
    :return: a dictionary of [orbital type, occupation] elements
    """
    occs = [[orb[0][1], orb[0][3]] for orb in basis_dict['bs']]
    result = {"s": [], "d": [], "f": [], "g": []}
    if any([occ[0] == 1 for occ in occs]):
        result["sp"] = []
    else:
        result["p"] = []
    for orb, e in occs:
        result[orbital_data[orb]["l"]].append(e)
    return result


def get_valence_orbitals(occs, vacant=False):
    """Returns the dictionary of valence orbital indices in occupations dict"""
    i_valence = {}
    for orb, occ in occs.items():
        n_valence_orb = -1
        for occ_i in occ:
            if occ_i == max_e[orb]:
                n_valence_orb += 1
            elif occ_i == 0 and not vacant:
                i_valence[orb] = n_valence_orb
                break
            else:
                i_valence[orb] = n_valence_orb + 1
                break
    return i_valence


def remove_valence_electrons(n, occs, element):
    """Removes n valence electrons from occupations dict"""
    # get valence orbitals
    i_valence = get_valence_orbitals(occs)
    shell_valence = get_valence_shell(element, n=1, vacant=False)
    # get electrons off last two orbitals
    for shell in shell_valence:
        orb = "sp" if shell in ("s", "p") and "sp" in i_valence else shell
        n_e = occs[orb][i_valence[orb]]
        if n_e >= n:
            # number of electrons is sufficient, remove electrons from the shell and break the loop
            occs[orb][i_valence[orb]] -= n
            n = 0
            break
        # number of electrons is not sufficient, remove all electrons from the shell and check another shell
        occs[orb][i_valence[orb]] -= n_e
        n -= n_e
    # if we get more electrons to remove, throw an error
    if n > 0:
        raise ValueError("Too large positive oxidation state for element {}: {}".format(
            element, n
        ))
    return occs


def add_valence_electrons(n, occs, element, high_spin_preferred):
    """Adds n valence electrons to occupation dict"""
    # get valence orbitals
    i_valence = get_valence_orbitals(occs)
    shell_valence = get_valence_shell(element, n=1, vacant=True)
    if high_spin_preferred:
        raise NotImplementedError
    # get electrons on last two orbitals
    for i_shell, shell in enumerate(shell_valence):
        orb = "sp" if shell in ("s", "p") and "sp" in i_valence else shell
        n_e = occs[orb][i_valence[orb]]
        if i_shell > 0 and n_e == max_e[orb]:
            # our bad, we erroneously found full orbitals as valence
            i_valence[orb] += 1
            n_e = 0
        if not high_spin_preferred and n + n_e <= max_e[orb]:
            # enough vacancies on the shell, fill'em and break the loop
            occs[orb][i_valence[orb]] += n
            n = 0
            break
        # not enough vacancies on the shell, fill the shell up to max_e and go into another iteration
        occs[orb][i_valence[orb]] += (max_e[orb] - n_e)
        n -= (max_e[orb] - n_e)
    # if after that we have more electrons to put on the shell, throw an error
    if n > 0:
        raise ValueError("Too large negative oxidation state for element {}: {}".format(
            element, n
        ))
    return occs
