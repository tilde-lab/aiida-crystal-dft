""" tests for the plugin that does not pollute your profiles/databases.
"""
import os

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
INPUT_FILES_DIR = os.path.join(TEST_DIR, 'input_files')
OUTPUT_FILES_DIR = os.path.join(TEST_DIR, 'output_files')

d12_input = {
    "label": "a title",
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
        },
        # "phonons": {"TEMPERAT": [273, 1073, 100],
        #             "info_print": ["ALL", "FREQ"],
        #             "INTENS": {
        #                 "technique": "INTPOL",
        #                 "INTRAMAN": {"INTCPHF": True,
        #                              "options": ["RAMANEXP", "NORENORM"]
        #                              },
        #             },
        #             "PREOPTGEOM": {
        #                 "type": "FULLOPTG",
        #                 "hessian": "HESSIDEN",
        #                 "gradient": "NUMGRATO",
        #             },
        #             },
        # "elastic_constants": {"type": "ELASTCON",
        #                       "convergence": {"TOLDEG": 0.0003},
        #                       "NUMDERIV": 3,
        #                       "STEPSIZE": 0.001
        #                       }
    },
    "basis_set": {
        "CHARGED": False,
    },
    "scf": {
        "dft": {
            # "xc": ["LDA", "PZ"],
            # or
            # "xc": "HSE06",
            # or
            "xc": {
                "LSRSH-PBE": [0.11, 0.25, 0.00001]
            },
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
            "EXCHPERM": True,
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
        # "fock_mixing": ["BROYDEN", 0.0001, 50, 2],
        "spinlock": {
            "SPINLOCK": [1, 10]
        },
        "post_scf": ["GRADCAL", "PPAN"]
    }
}

d12_expected = """a title
EXTERNAL
ATOMSYMM
SYMMOPS
STRUCPRT
OPTGEOM
FULLOPTG
HESSIDEN
NUMGRATO
PRINTOPT
PRINTFORCES
TOLDEG
0.0003
TOLDEX
0.0012
TOLDEE
7
MAXCYCLE
50
FINALRUN
4
ENDOPT
BASISSET
STO-3G
DFT
LSRSH-PBE
0.11  0.25  1e-05
SPIN
XLGRID
BECKE
TOLLDENS
6
TOLLGRID
14
LIMBEK
400
END
SHRINK
8 8
BIPOLAR
18  14
BIPOSIZE
4000000
EXCHSIZE
4000000
EXCHPERM
ILASIZE
6000
INTGPACK
0
MADELIND
50
POLEORDR
4
TOLINTEG
6  6  6  6  12
TOLPSEUD
6
FMIXING
0
MAXCYCLE
50
TOLDEE
6
LEVSHIFT
2  1
SMEAR
0.1
DIIS
SPINLOCK
1  10
GRADCAL
PPAN
END
"""