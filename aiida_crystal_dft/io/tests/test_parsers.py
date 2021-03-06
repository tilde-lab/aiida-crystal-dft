#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Tests for pyparsing-based parsers
"""

from ..parsers import d12_geometry_parser, gto_basis_parser


def test_geometry_parser():
    d12 = """a title
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
MAXCYCLE
50
TOLDEX
0.0012
FINALRUN
4
TOLDEG
0.0003
TOLDEE
7
FRAGMENT
2
1 3 
ENDOPT
END
12 3
1 0 3  2.  0.
1 1 3  8.  0.
1 1 3  2.  0.
8 8
0 0 6 2.0 1.0
 27032.382631 0.00021726302465
 4052.3871392 0.00168386621990
 922.32722710 0.00873956162650
 261.24070989 0.03523996880800
 85.354641351 0.11153519115000
 31.035035245 0.25588953961000
0 0 2 2.0 1.0
 12.260860728 0.39768730901000
 4.9987076005 0.24627849430000
0 0 1 0.0 1.0
 1.0987136000 1.00000000000000
0 0 1 0.0 1.0
 0.3565870100 1.00000000000000
0 2 4 4.0 1.0
 63.274954801 0.0060685103418
 14.627049379 0.0419125758240
 4.4501223456 0.1615384108800
 1.5275799647 0.3570695131100
0 2 1 0.0 1.0
 0.5489735000 1.0000000000000
0 2 1 0.0 1.0
 0.1858671100 1.0000000000000
0 3 1 0.0 1.0
 0.2534621300 1.0000000000000
99 0
CHARGED
GHOSTS
2
5 6 
END
DFT
EXCHANGE
LDA
CORRELAT
PZ
SPIN
XLGRID
BECKE
TOLLDENS
6
LIMBEK
400
TOLLGRID
14
END
SHRINK
8 8
INTGPACK
0
FMIXING
0
EXCHPERM
SMEAR
0.1
TOLPSEUD
6
POLEORDR
4
EXCHSIZE
4000000
ILASIZE
6000
MAXCYCLE
50
BIPOLAR
18 14
MADELIND
50
TOLINTEG
6 6 6 6 12
BIPOSIZE
4000000
LEVSHIFT
2 1
TOLDEE
6
DIIS
SPINLOCK
1 10
ATOMSPIN
4
1 1
2 -1
3 1
4 -1
GRADCAL
PPAN
END
"""
    parser = d12_geometry_parser()
    res = parser.parseString(d12)
    for r_i in res:
        print(r_i)


def test_basis_parser():
    basis = """
47 6
HAYWSC
0 1 2   8.0  1.00
 5.8231   0.5286  -0.4178
 4.8342  -1.0470   0.1120
0 1 1   1.0  1.00
 1.8530   1.0000   1.0000
0 1 1   0.0  1.00
 0.7715   1.0000   1.0000
0 1 1   0.0  1.00
 0.1200   1.0000   1.0000
0 3 3  10.0  1.00
21.3210  -0.0140
 2.6260   2.4560
 1.0070   4.6721
0 3 1   0.0  1.00
 0.3110   1.0000
    """
    parser = gto_basis_parser()
    res = parser.parseString(basis)
    assert res['ecp'][0] == "HAYWSC"
    assert res['bs'][0][0][3] == 8.


def test_basis_parser_issue_39():
    basis = """
22 9
0  0  8  2.  1.
 225338        0.000228
 32315         0.001929
 6883.61       0.011100
 1802.14       0.05
 543.063       0.17010
 187.549       0.369
 73.2133       0.4033
 30.3718       0.1445
0 1 6 8. 1.
 554.042      -0.0059       0.0085
 132.525      -0.0683       0.0603
 43.6801      -0.1245       0.2124
17.2243       0.2532       0.3902
 7.2248        0.6261       0.4097
 2.4117        0.282        0.2181
0 1 4 8. 1.
 24.4975       0.0175      -0.0207
 11.4772      -0.2277      -0.0653
 4.4653       -0.7946       0.1919
 1.8904        1.0107       1.3778
0 1 1 2. 1.
 0.790008359901 1. 1.
0 1 1 0. 1.
 0.35160337936 1. 1.
0 3 3 2. 1.
 8.89621398666 0.163566701992
 2.76266406164 0.444392907716
 1.0600606657 0.505403203892
0 3 1 0. 1.
 0.858484740501  1.
0 3 1 0. 1
 0.486945513149 1.
0 4 1 0. 1
 0.633249434959 1.
"""
    parser = gto_basis_parser()
    res = parser.parseString(basis)
    assert res['bs'][0][1][0] == 225338
