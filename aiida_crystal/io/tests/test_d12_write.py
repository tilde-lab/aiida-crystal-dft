import pytest
from aiida_crystal.io.d12_write import write_input
# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import test_basis_family_predefined


@pytest.mark.skip
def test_input_full(test_basis_family_predefined):
    from aiida_crystal.tests import d12_input, d12_expected
    outstr = write_input(d12_input, test_basis_family_predefined)
    assert outstr == d12_expected


def test_input_with_atom_props():
    class Basis:
        def __init__(self, content):
            self.content = content

    indict = {
        "scf": {
            "k_points": [16, 8]
        },
        "geometry": {
            "optimise": {
                "type": "FULLOPTG"
            }
        }
    }

    atomprops = {
        "spin_alpha": [1, 3],
        "spin_beta": [2, 4],
        "unfixed": [1, 3],
        "ghosts": [5, 6]
    }

    basis_set1 = Basis("basis_set1")
    basis_set2 = Basis("basis_set2")
    outstr = write_input(indict, [basis_set1, basis_set2], atomprops)
    expected = """CRYSTAL run
EXTERNAL
OPTGEOM
FULLOPTG
FRAGMENT
2
1 3 
ENDOPT
END
basis_set1
basis_set2
99 0
GHOSTS
2
5 6 
END
SHRINK
16 8
ATOMSPIN
4
1 1
2 -1
3 1
4 -1
END
"""
    for out, exp in zip(outstr.split('\n'), expected.split('\n')):
        assert out == exp
