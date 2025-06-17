#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

"""
A module describing the CRYSTAL basis family (Str on steroids)
"""
import os
from collections import Counter
from ase.data import atomic_numbers, chemical_symbols
from aiida.orm import Group, Data
from aiida.plugins import DataFactory
from aiida_crystal_dft.utils import get_automatic_user
from aiida_crystal_dft.data.basis import CrystalBasisData


# predefined basis sets in CRYSTAL17
BASIS_FAMILY_KWDS = {
    "STO-3G": list(range(1, 54)),
    "STO-6G": list(range(1, 37)),
    "POB-DZVP": list(range(1, 36)) + [49, 74],
    "POB-DZVPP": list(range(1, 36)) + [49, 83],
    "POB-TZVP": list(range(1, 36)) + [49, 83]
}

BASIS_FAMILY_TYPE = 'crystal_dft.basis_family'


class CrystalBasisFamilyData(Data):

    def __init__(self, **kwargs):
        """The Data class for CRYSTAL basis family"""
        name = kwargs.pop('name', None)
        super(CrystalBasisFamilyData, self).__init__(**kwargs)
        if name is not None:
            self.set_name(name)
        self.structure = None
        self.oxi_states = None

    @classmethod
    def _get(cls, name=None):
        # check if we can find the basis family
        from aiida.orm.querybuilder import QueryBuilder
        qb = QueryBuilder()
        filters = {}
        if name is not None:
            filters['attributes.name'] = {'==': name}
        qb.append(cls, filters=filters)
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
        instance = cls()
        instance.set_name(name=name)
        instance.store()
        if basis_sets is not None:
            instance.add(basis_sets)
        return instance, True

    def add(self, basis_sets):
        """Adds basis sets to family"""
        group, group_created = Group.collection.get_or_create(label=self.name,
                                                           type_string=BASIS_FAMILY_TYPE,
                                                           user=get_automatic_user())
        # validate basis sets
        if not all([isinstance(basis, CrystalBasisData) for basis in basis_sets]):
            raise TypeError('Basis sets not of type CrystalBasisData can not be added to basis family {}'.
                            format(self.name))
        elements = [basis.element for basis in basis_sets]
        if len(set(elements)) != len(elements):
            several_bases = [el for el, n in Counter(elements).items() if n > 1]
            raise ValueError("Trying to add more than one basis set for element(s): {} to basis family {}".
                             format(", ".join(several_bases), self.name))
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
        _group, _ = Group.collection.get_or_create(label=self.name,
                                                type_string=BASIS_FAMILY_TYPE,
                                                user=get_automatic_user())
        return _group

    @property
    def name(self):
        return self.base.attributes.get("name", default=None)

    @name.setter
    def name(self, value):
        self.base.attributes.set("name", value)

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
                raise ValueError('Basis sets for some elements present in the structure not found in family: {}'.format(
                    ",".join(list(set(composition).difference(elements_in_group)))))
            self.oxi_states = {el: 0. for el in composition}
        self.structure = structure

    def set_oxistates(self, oxi_states):
        if self.structure is None:
            raise ValueError("Structure must be set before setting oxidation states")
        composition = self.structure.get_composition()
        if not all([el in oxi_states for el in composition]):
            raise ValueError("Oxidation states missing for the following elements: {}".format(
                [el for el in composition if el not in oxi_states]
            ))
        if sum([oxi_states[el]*composition[el] for el in composition]) != 0:
            raise ValueError("Unit cell not neutral for the following oxidation states: {}".format(oxi_states))
        self.oxi_states = oxi_states

    def get_bases(self, structure=None):
        if self.predefined:
            return []
        if structure is None:
            if self.structure is None:
                raise ValueError('Structure is needed to be set for the basis family')
            else:
                structure = self.structure
        elif self.structure is None:
            # for oxi_states to be set to default
            self.set_structure(structure)
        composition = structure.get_composition()
        return [self.get_basis(el) for el in sorted(composition.keys(), key=lambda k: atomic_numbers[k])]

    @property
    def predefined(self):
        return self.name in BASIS_FAMILY_KWDS

    @property
    def content(self):
        """Content for adding to .d12
        """
        if self.predefined:
            return "BASISSET\n{}\n".format(self.name)
        bases = self.get_bases()
        oxi_states = [self.oxi_states[el] for el in sorted(self.oxi_states.keys(), key=lambda k: atomic_numbers[k])]
        basis_strings = [b.content(state) for b, state in zip(bases, oxi_states)]
        basis_strings.append("99 0\n")
        return "\n".join(basis_strings)

    def store(self):
        return super(CrystalBasisFamilyData, self).store()

    @classmethod
    def create_predefined(cls):
        """Create predefined basis families"""
        created = []
        for name in BASIS_FAMILY_KWDS:
            _, flag = cls.get_or_create(name)
            if flag:
                created.append(name)
        return created

    @classmethod
    def upload(cls, name, path, extension='basis', description=None):
        """
        Upload a basis family
        :param name: a name of the basis family (should not coincide with predefined)
        :param path: a path with basis files
        :param extension: a extension of basis files
        :param description: an (optional) description of basis family
        :return: numbers of files found; flag showing if group is created; the set of elements for which a basis set
        was uploaded
        """
        if name in BASIS_FAMILY_KWDS:
            raise NameError('{} is in the list of predefined basis families'.format(name))
        files = [
            os.path.realpath(os.path.join(path, i))
            for i in os.listdir(path)
            if (os.path.isfile(os.path.join(path, i))
                and i.lower().endswith(extension))
        ]
        bases = [CrystalBasisData.from_file(file_name) for file_name in files]
        group, created = cls.get_or_create(name)
        if description is not None:
            group.description = description
        added = group.add(bases)
        return len(files), created, added

    @classmethod
    def get_families(cls, filter_elements=None, user=None):
        """
        Return all names of groups of type BasisFamily, possibly with some filters.

        :param filter_elements: A string or a list of strings.
               If present, returns only the groups that contains one Basis for
               every element present in the list. Default=None, meaning that
               all families are returned.
        :param user: if None (default), return the groups for all users.
               If defined, it should be either a DbUser instance, or a string
               for the username (that is, the user email).
        """
        from aiida.orm import Group
        group_query_params = {"type_string": BASIS_FAMILY_TYPE}
        if user is not None:
            group_query_params['user'] = user
        basis_groups = Group.collection.find(filters=group_query_params)
        predefined_bases = [b for b in cls._get() if b.predefined]
        if isinstance(filter_elements, str):
            filter_elements = [filter_elements]
        if filter_elements is not None:
            actual_filter_elements = {_.capitalize() for _ in filter_elements}
            basis_groups = [g for g in basis_groups if actual_filter_elements.issubset({b.element for b in g.nodes})]
            predefined_bases = [b for b in predefined_bases if
                                actual_filter_elements.issubset({chemical_symbols[n]
                                                                 for n in BASIS_FAMILY_KWDS[b.name]})]
        # Sort by name
        basis_groups.sort(key=lambda x: x.label)
        predefined_bases.sort(key=lambda x: x.name)
        # Return the predefined bases and groups, without name
        return predefined_bases, basis_groups
