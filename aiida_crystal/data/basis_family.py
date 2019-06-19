#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
A module describing the CRYSTAL basis family (Str on steroids)
"""
from ase.data import atomic_numbers
from aiida.orm import Group, DataFactory
from aiida.orm.data import Data
from aiida_crystal.aiida_compatibility import get_automatic_user
from aiida_crystal.data.basis import CrystalBasisData

BASIS_FAMILY_KWDS = [
    "STO-3G",
    "STO-6G",
    "POB-DZVP",
    "POB-DZVPP",
    "POB-TZVP"
]

BASIS_FAMILY_TYPE = 'crystal.basis_family'


class CrystalBasisFamilyData(Data):

    @classmethod
    def _get(cls, name):
        # check if we can find the basis family
        from aiida.orm.querybuilder import QueryBuilder
        qb = QueryBuilder()
        qb.append(cls, filters={'attributes.name': {'==': name}})
        return [res for [res] in qb.all()]

    @classmethod
    def get_or_create(cls, name, basis_sets=None):
        """
        The class method gets the basis family or creates it if it's not existent
        :param name: basis family name
        :param basis_sets: an iterable of basis sets to add to group
        :return: the CrystalBasisFamilyData instance, flag showing if the basis family was created anew
        """
        found = cls._get(name)
        if found:
            return found[0], False

        # creating basis family
        if name in BASIS_FAMILY_KWDS:
            if basis_sets is not None:
                raise ValueError("{} is a predefined basis family in CRYSTAL; can't add basis sets to it".format(name))
        # if the name is not found and is not predefined
        instance = cls(name=name).store()
        if basis_sets is not None:
            instance.add(basis_sets)
        return instance, True

    def add(self, basis_sets):
        """Adds basis sets to family"""
        group, group_created = Group.get_or_create(name=self.name,
                                                   type_string=BASIS_FAMILY_TYPE,
                                                   user=get_automatic_user())
        # validate basis sets
        if not all([isinstance(basis, CrystalBasisData) for basis in basis_sets]):
            raise TypeError('Basis sets not of type CrystalBasisData can not be added to basis family {}'.
                            format(self.name))
        elements = [basis.element for basis in basis_sets]
        if len(set(elements)) != len(elements):
            raise ValueError("Trying to add more than one basis set for some element to basis family {}".
                             format(self.name))
        # check for element uniqueness within the existent group
        if not group_created:
            elements_in_group = set([basis.element for basis in group.nodes])
            elements_to_add = set(elements).difference(elements_in_group)
        else:
            elements_to_add = set(elements)
        group.add_nodes([basis for basis in basis_sets if basis.element in elements_to_add])
        return elements_to_add

    def get_basis(self, element):
        """If basis family is not predefined, return the basis set corresponding to element"""
        if self.predefined:
            raise TypeError('Cannot retrieve basis sets from predefined basis family')
        for basis in self.group.nodes:
            if basis.element == element:
                return basis
        raise ValueError('No basis for element {} found in family {}'.format(element, self.name))

    @property
    def group(self):
        _group, _ = Group.get_or_create(name=self.name,
                                        type_string=BASIS_FAMILY_TYPE,
                                        user=get_automatic_user())
        return _group

    @property
    def name(self):
        return self.get_attr("name", default=None)

    @name.setter
    def name(self, value):
        self._set_attr("name", value)

    def set_name(self, name):
        # check name for this instance
        if self.name is not None:
            raise ValueError("Name has already been set for this {} instance".format(self.__class__.__name__))
        # check uniqueness
        found = self._get(name)
        if found and found[0].uuid != self.uuid:
            raise ValueError("Found another {} instance in db with different uuid".format(self.__class__.__name__))
        self.name = name

    def set_structure(self, structure):
        if not isinstance(structure, DataFactory('structure')):
            raise TypeError('Structure must be set with StructureData object in basis family')
        if not self.predefined:
            # check if all elements have their bases in the family
            composition = structure.get_composition()
            elements_in_group = set([basis.element for basis in self.group.nodes])
            if not all([el in elements_in_group for el in composition]):
                raise ValueError('Basis sets for some elements present in the structure not found in family ')
        self.structure = structure

    @property
    def predefined(self):
        return self.name in BASIS_FAMILY_KWDS

    @property
    def content(self):
        """Content for adding to .d12
        """
        if self.predefined:
            return "BASISSET\n{}\n".format(self.name)
        if not hasattr(self, 'structure'):
            raise AttributeError('Structure is needed to be set for the basis family')
        composition = self.structure.get_composition()
        basis_strings = [self.get_basis(element).content for element in sorted(composition.keys(),
                                                                         key=lambda k: atomic_numbers[k])]
        basis_strings.append("99 0")
        return "\n".join(basis_strings)

    def store(self, with_transaction=True, use_cache=None):
        return super(CrystalBasisFamilyData, self).store(with_transaction=with_transaction,
                                                         use_cache=use_cache)
