#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A collection of pyparsing-based block parsers
"""

import pyparsing as pp

pc = pp.pyparsing_common


def d12_geometry_parser():
    """Geometry block parser"""
    title = pp.restOfLine()('title')
    return title


def gto_basis_parser():
    """
    Gaussian-type orbital basis parser with pyparsing
    Basis structure in CRYSTAL is as follows:
    NUM  NSHELLS
    <ECP_PART>
    <SHELL_PART>
    <PRIMITIVE_PART>

    :return: basis parser
    """
    header = 2 * pc.integer
    ecp_part = pp.Word(pp.alphas) + pp.Optional(pp.Group(pc.real + 6 * pc.integer) +
                                                pp.Group(pp.OneOrMore(pp.Group(2 * pc.real + pc.signed_integer))))
    bs_head = pp.Group(3 * pc.integer + 2 * pc.number)
    bs_part = pp.OneOrMore(pp.Group(bs_head +
                                    pp.ZeroOrMore(pp.Group((3 * pc.real + pp.Suppress(pp.LineEnd())) ^
                                                           (2 * pc.real + pp.Suppress(pp.LineEnd()))))))
    return pp.SkipTo(header) + header('header') + pp.Optional(ecp_part('ecp')) + bs_part('bs')
