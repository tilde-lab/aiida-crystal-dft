#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.

"""
A module containing data on electrons and oxidation states of the elements
"""
from itertools import product
from ase.data import atomic_numbers

# Common oxidation states have larger weight
# see https://en.wikipedia.org/wiki/Oxidation_state
oxistate_weights = [
    {},  # X
    {-1: 2, 1: 2},  # H
    {},  # He
    {1: 2},  # Li
    {0: 1, 1: 1, 2: 2},  # Be
    {-5: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 2},  # B
    {-4: 2, -3: 2, -2: 2, -1: 2, 0: 1, 1: 2, 2: 2, 3: 2, 4: 2},  # C
    {-3: 2, -2: 1, -1: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 2},  # N
    {-2: 2, -1: 1, 0: 1, 1: 1, 2: 1},  # O
    {-1: 2},  # F
    {},  # Ne
    {-1: 1, 1: 2},  # Na
    {0: 1, 1: 1, 2: 2},  # Mg
    {-2: 1, -1: 1, 1: 1, 2: 1, 3: 2},  # Al
    {-4: 2, -3: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 2},  # Si
    {-3: 2, -2: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 2},  # P
    {-2: 2, -1: 1, 0: 1, 1: 1, 2: 2, 3: 1, 4: 2, 5: 1, 6: 2},  # S
    {-1: 2, 1: 2, 2: 1, 3: 2, 4: 1, 5: 2, 6: 1, 7: 2},  # Cl
    {0: 1},  # Ar
    {-1: 1, 1: 2},  # K
    {1: 1, 2: 2},  # Ca
    {0: 1, 1: 1, 2: 1, 3: 2},  # Sc
    {-2: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 2},  # Ti
    {-3: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2},  # V
    {-4: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 1, 6: 2},  # Cr
    {-3: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 2, 3: 1, 4: 2, 5: 1, 6: 1, 7: 2},  # Mn
    {-4: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 2, 3: 2, 4: 1, 5: 1, 6: 2, 7: 1},  # Fe
    {-3: 1, -1: 1, 0: 1, 1: 1, 2: 2, 3: 2, 4: 1, 5: 1},  # Co
    {-2: 1, -1: 1, 0: 1, 1: 1, 2: 2, 3: 1, 4: 1},  # Ni
    {-2: 1, 0: 1, 1: 1, 2: 2, 3: 1, 4: 1},  # Cu
    {-2: 1, 1: 1, 2: 2},  # Zn
    {-5: 1, -4: 1, -3: 1, -2: 1, -1: 1, 1: 1, 2: 1, 3: 2},  # Ga
    {-4: 2, -3: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 2, 3: 1, 4: 2},  # Ge
    {-3: 2, -2: 1, -1: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 2},  # As
    {-2: 2, -1: 1, 1: 1, 2: 2, 3: 1, 4: 2, 5: 1, 6: 2},  # Se
    {-1: 2, 1: 2, 3: 2, 4: 1, 5: 2, 7: 2},  # Br
    {0: 2, 1: 1, 2: 1},  # Kr
    {-1: 1, 1: 2},  # Rb
    {1: 1, 2: 2},  # Sr
    {0: 1, 1: 1, 2: 1, 3: 2},  # Y
    {-2: 1, 1: 1, 2: 1, 3: 1, 4: 2},  # Zr
    {-3: 1, -1: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2},  # Nb
    {-4: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 1, 6: 2},  # Mo
    {-3: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 1, 6: 1, 7: 2},  # Tc
    {-4: 1, -2: 1, 0: 1, 1: 1, 2: 2, 3: 2, 4: 2, 5: 1, 6: 1, 7: 1, 8: 1},  # Ru
    {-3: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 1, 6: 1},  # Rh
    {0: 1, 1: 1, 2: 2, 3: 1, 4: 2},  # Pd
    {-2: 1, -1: 1, 1: 2, 2: 1, 3: 1},  # Ag
    {-2: 1, 1: 1, 2: 2},  # Cd
    {-5: 1, -2: 1, -1: 1, 1: 1, 2: 1, 3: 2},  # In
    {-4: 2, -3: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 2, 3: 1, 4: 2},  # Sn
    {-3: 2, -2: 1, -1: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 2},  # Sb
    {-2: 2, -1: 1, 1: 1, 2: 2, 3: 1, 4: 2, 5: 1, 6: 2},  # Te
    {-1: 2, 1: 2, 3: 2, 4: 1, 5: 2, 6: 1, 7: 2},  # I
    {0: 2, 1: 1, 2: 1, 4: 2, 6: 2, 8: 2},  # Xe
    {-1: 1, 1: 2},  # Cs
    {1: 1, 2: 2},  # Ba
    {0: 1, 1: 1, 2: 1, 3: 2},  # La
    {2: 1, 3: 2, 4: 2},  # Ce
    {0: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 1},  # Pr
    {0: 1, 2: 1, 3: 2, 4: 1},  # Nd
    {2: 1, 3: 2},  # Pm
    {0: 1, 2: 1, 3: 2},  # Sm
    {2: 2, 3: 2},  # Eu
    {0: 1, 1: 1, 2: 1, 3: 2},  # Gd
    {0: 1, 1: 1, 2: 1, 3: 2, 4: 1},  # Tb
    {0: 1, 2: 1, 3: 2, 4: 1},  # Dy
    {0: 1, 2: 1, 3: 2},  # Ho
    {0: 1, 2: 1, 3: 2},  # Er
    {2: 1, 3: 2},  # Tm
    {2: 1, 3: 2},  # Yb
    {0: 1, 2: 1, 3: 2},  # Lu
    {-2: 1, 1: 1, 2: 1, 3: 1, 4: 2},  # Hf
    {-3: 1, -1: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2},  # Ta
    {-4: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 1, 6: 2},  # W
    {-3: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 1, 6: 1, 7: 1},  # Re
    {-4: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 1, 6: 1, 7: 1, 8: 1},  # Os
    {-3: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 2, 4: 2, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},  # Ir
    {-3: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 2, 3: 1, 4: 2, 5: 1, 6: 1},  # Pt
    {-3: 1, -2: 1, -1: 1, 0: 1, 1: 1, 2: 1, 3: 2, 5: 1},  # Au
    {-2: 1, 1: 2, 2: 2},  # Hg
    {-5: 1, -2: 1, -1: 1, 1: 2, 2: 1, 3: 2},  # Tl
    {-4: 1, -2: 1, -1: 1, 1: 1, 2: 2, 3: 1, 4: 2},  # Pb
    {-3: 1, -2: 1, -1: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 1},  # Bi
    {-2: 2, 2: 2, 4: 2, 5: 1, 6: 1},  # Po
    {-1: 2, 1: 2, 3: 1, 5: 1, 7: 1},  # At
    {2: 2, 6: 1},  # Rn
    {1: 2},  # Fr
    {2: 2},  # Ra
    {3: 2},  # Ac
    {1: 1, 2: 1, 3: 1, 4: 2},  # Th
    {3: 1, 4: 1, 5: 2},  # Pa
    {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2},  # U
    {2: 1, 3: 1, 4: 1, 5: 2, 6: 1, 7: 1},  # Np
    {2: 1, 3: 1, 4: 2, 5: 1, 6: 1, 7: 1},  # Pu
    {2: 1, 3: 2, 4: 1, 5: 1, 6: 1, 7: 1},  # Am
    {3: 2, 4: 1, 5: 1, 6: 1},  # Cm
    {3: 2, 4: 1, 5: 1},  # Bk
    {2: 1, 3: 2, 4: 1, 5: 1},  # Cf
    {2: 1, 3: 2, 4: 1},  # Es
    {2: 1, 3: 2},  # Fm
    {2: 1, 3: 2},  # Md
    {2: 2, 3: 1},  # No
    {3: 2}   # Lr
]

oxistates = [os.keys() for os in oxistate_weights]

orbital_data = [{"l": "s", "max_e": 2},
                {"l": "sp", "max_e": 8},
                {"l": "p", "max_e": 6},
                {"l": "d", "max_e": 10},
                {"l": "f", "max_e": 14},
                {"l": "g", "max_e": 18}
                ]

orbitals = ["1s", "2s", "2p", "3s", "3p", "4s", "3d", "4p", "5s",
            "4d", "5p", "6s", "4f", "5d", "6p", "7s", "5f", "6d", "7p"]

max_e = {orb["l"]: orb["max_e"] for orb in orbital_data}


def get_valence_shell(element, n=0, vacant=False):
    """Returns valence shell (plus n shells, vacant or not) for the given element"""
    n_e = atomic_numbers[element]
    i = 0
    while n_e > 0:
        orb = orbitals[i][1]
        n_e -= max_e[orb]
        if n_e > 0:
            i += 1
    if vacant:
        return [x[1] for x in orbitals[i:i+n+1]]
    if i <= n:
        return [x[1] for x in orbitals[i::-1]]
    return [x[1] for x in orbitals[i:i-n-1:-1]]


def electronic_config(element, crystal_format=False, sp=False):
    """
    Constructs the ground state electronic configuration for the given element
    :param element: A one- or two-letter element name
    :param crystal_format: (default: False) whether to return conventional electronic configuration (a list containing
    orbital populations from least energetic to most energetic) or the configuration in CRYSTAL format (a dictionary
    of lists with orbital l numbers as keys)
    :param sp: (works only in conjunction with crystal_format, default: False) if True, merges s- and p-orbitals
    into single sp-orbital
    :return: A list or dict representing ground-state electronic configuration for the given element
    """
    def helper(e, result):
        """A helper recursive function for conventional electronic config"""
        orb = orbitals[len(result)][1]
        if e <= max_e[orb]:
            result.append(e)
            return result
        result.append(max_e[orb])
        return helper(e - max_e[orb], result)

    def helper_crystal(e, i_orb, result):
        """A helper recursive function for CRYSTAL format electronic config"""
        n, orb = orbitals[i_orb]
        n = int(n)
        max_e_orb = max_e[orb]
        if sp and n > 1 and orb in ("s", "p"):
            orb = "sp"
        # last orbital
        if e <= max_e_orb:
            if orb == "sp" and len(result[orb]) == n-1:
                result[orb][-1] += e
            else:
                result[orb].append(e)
            return result
        if orb == "sp" and len(result[orb]) == n-1:
            result[orb][-1] += max_e_orb
        else:
            result[orb].append(max_e_orb)
        return helper_crystal(e - max_e_orb, i_orb + 1, result)

    # actual function run
    if not crystal_format:
        return helper(atomic_numbers[element], [])
    # crystal format case
    if not sp:
        return helper_crystal(atomic_numbers[element], 0, {"s": [], "p": [], "d": [], "f": []})
    # crystal helper with sp orbitals case
    return helper_crystal(atomic_numbers[element], 0, {"s": [], "sp": [], "d": [], "f": []})


def guess_oxistates(structure):
    """A function returning a dictionary of oxidation states for each element of the structure"""
    composition = structure.get_composition()
    elements = composition.keys()
    oxistates_element = [oxistates[atomic_numbers[el]] for el in elements]
    weights = {state: sum([composition[el] * oxistate_weights[atomic_numbers[el]][state[i]]
                           for i, el in enumerate(elements)])
               for state in product(*oxistates_element)
               if sum([x*y for x, y in zip(state, [composition[el] for el in elements])]) == 0}
    if not weights:
        raise ValueError("No electrically neutral state found for the following composition: {}".format(composition))
    return dict(zip(elements, sorted(weights.items(), key=lambda x: x[1], reverse=True)[0][0]))


def guess_spinlock(structure):
    """A function that tries to guess total spin of structure in case it is magnetic.
    Works only with 3d and 4f elements"""
    # get primitive structure
    from aiida_crystal_dft.utils.geometry import to_primitive
    composition = to_primitive(structure).get_composition()
    elements = composition.keys()
    # change valence electron number based on oxidation states
    oxi_states = guess_oxistates(structure)
    valence = {e: (electronic_config(e)[-1] - oxi_states[e], get_valence_shell(e)[0]) for e in elements}
    # guess spinlock based on oxidation state and composition
    transition_els = [e for e in elements if valence[e][1] in ('d', 'f')]
    if not transition_els:
        # no transition elements in structure, are nonmagnetic as of now
        return 0
    return sum([composition[el] * unpaired_electrons(*valence[el]) for el in transition_els])


def unpaired_electrons(n_e, shell):
    """Returns the number of unpaired electrons out of n_e on the shell according to Hund rule"""
    return max_e[shell]/2 - abs(n_e - max_e[shell]/2)

