#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A parser for fort.25 bands and DOS files
"""
import numpy as np
from pyparsing import *

pc = pyparsing_common


def _parse_string(parser, string):
    try:
        parsed_data = parser.parseString(string)
    except ParseException as pe:
        # complete the error message
        msg = "ERROR during parsing of line %d:" % pe.lineno
        msg += '\n' + '-' * 40 + '\n'
        msg += pe.line + '\n'
        msg += ' ' * (pe.col - 1) + '^\n'
        msg += '-' * 40 + '\n' + pe.msg
        pe.msg = msg
        raise
    return parsed_data


def band_parser():
    header = (pc.integer + Word(alphas) + 2*pc.integer + 3*pc.sci_real).setResultsName('header')
    e = (2*pc.sci_real).setResultsName('energy')
    k_path = (6*pc.integer).setResultsName('k_path')
    bands = OneOrMore(pc.sci_real).setResultsName('bands')
    return header + e + k_path + bands


class Fort25(object):

    def __init__(self, file_name):
        with open(file_name, 'r') as f:
            self._data = f.read().split('-%-')

    def parse(self):
        band_data = [bloc for bloc in self._data if bloc[1:5] == 'BAND']
        return self._parse_bands(band_data)

    def _parse_bands(self, data):
        labels = []
        bands = []
        for datum in data:
            parsed_data = _parse_string(band_parser(), datum)
            num_bands = parsed_data["header"][2]
            num_k = parsed_data["header"][3]
            k_start = tuple(parsed_data["k_path"][:3])
            k_end = tuple(parsed_data["k_path"][3:])
            # work with labels
            if not labels:
                labels.append(str(k_start))
            labels += ['' for _ in range(num_k - 2)]
            labels.append(str(k_end))
            bands.append(np.array(parsed_data["bands"].asList()).reshape(num_k, num_bands))
        return labels, np.vstack(bands)
