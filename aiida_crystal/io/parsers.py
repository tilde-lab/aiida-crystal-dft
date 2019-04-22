#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A collection of pyparsing-based block parsers
"""

import pyparsing as pp
pc = pp.pyparsing_common


def d12_geometry_parser():
    """Geometry block parser"""
    title = pp.restOfLine()('title')
    external = pp.Word(pp.alphas)('external')

    return title