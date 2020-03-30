"""
test d12 schema
"""
import pytest
from aiida_crystal_dft.schemas import validate_with_json
from jsonschema import ValidationError


def test_toplevel_fail():
    with pytest.raises(ValidationError):
        validate_with_json({})
    with pytest.raises(ValidationError):
        validate_with_json({"a": 1})


def test_toplevel_pass():
    data = {
        # "title": "a title",
        # "geometry": {},
        # "basis_set": {},
        "scf": {
            "k_points": [8, 8]
        }
    }
    validate_with_json(data)


def test_full_pass():
    data = {
        "title": "a title",
        "geometry": {
            "info_print": ["ATOMSYMM", "SYMMOPS"],
            "info_external": ["STRUCPRT"],
            "optimise": {
                "type": "FULLOPTG",
                "hessian": "HESSIDEN",
                "gradient": "NUMGRATO",
                "info_print": ["PRINTOPT", "PRINTFORCES"],
                "convergence": {
                    "TOLDEG": 0.0003,
                    "TOLDEX": 0.0012,
                    "TOLDEE": 7,
                    "MAXCYCLE": 50,
                    "FINALRUN": 4
                },
            }
        },
        "basis_set": {
            "CHARGED": False,
        },
        "scf": {
            "dft": {
                "xc": ["LDA", "PZ"],
                # or
                # "xc": "HSE06",
                # or
                # "xc": {"LSRSH-PBE": [0.11, 0.25, 0.00001]},
                "SPIN": True,
                "grid": "XLGRID",
                "grid_weights": "BECKE",
                "numerical": {
                    "TOLLDENS": 6,
                    "TOLLGRID": 14,
                    "LIMBEK": 400
                }
            },
            # or
            # "single": "UHF",
            "k_points": [8, 8],
            "numerical": {
                "BIPOLAR": [18, 14],
                "BIPOSIZE": 4000000,
                "EXCHSIZE": 4000000,
                "EXCHPERM": False,
                "ILASIZE": 6000,
                "INTGPACK": 0,
                "MADELIND": 50,
                "NOBIPCOU": False,
                "NOBIPEXCH": False,
                "NOBIPOLA": False,
                "POLEORDR": 4,
                "TOLINTEG": [6, 6, 6, 6, 12],
                "TOLPSEUD": 6,
                "FMIXING": 0,
                "MAXCYCLE": 50,
                "TOLDEE": 6,
                "LEVSHIFT": [2, 1],
                "SMEAR": 0.1
            },
            "fock_mixing": "DIIS",
            # or
            # "fock_mixing": {"BROYDEN": [0.0001, 50, 2]},
            "spinlock": {
                "SPINLOCK": [1, 10]
            },
            "post_scf": ["GRADCAL", "PPAN"]
        }
    }
    validate_with_json(data)
from aiida_crystal_dft.io.d12_write import write_input
# noinspection PyUnresolvedReferences
from aiida_crystal_dft.tests.fixtures import test_basis_family_predefined


@pytest.mark.skip
def test_input_full(test_basis_family_predefined):
    from aiida_crystal_dft.tests import d12_input, d12_expected
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
