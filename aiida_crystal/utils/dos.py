#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Utility functions for automatic generation of density of states projections
"""
from collections import defaultdict


def get_dos_projections_atoms(numbers):
    # DOS is projected on atoms in the basis set order
    result = defaultdict(list)
    for i, n in enumerate(numbers):
        result[n].append(i + 1)
    return [result[n] for n in set(numbers)]
