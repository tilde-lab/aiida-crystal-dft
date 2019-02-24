#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A parser for fort.25 bands and DOS files
"""
import numpy as np
from pyparsing import *

pc = pyparsing_common

__all__ = ["Fort25"]


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
        # the resulting dictionary
        result = {"bands": {}}
        # band structure
        band_data = [bloc for bloc in self._data if bloc[1:5] == 'BAND']
        result["bands"] = self._parse_bands(band_data)
        return result

    def _parse_bands(self, data):
        bands = []
        result = {"n_bands": 0,
                  "n_k": [],
                  "path": [],
                  "bands": None}
        for datum in data:
            parsed_data = _parse_string(band_parser(), datum)
            if not result["n_bands"]:
                result["n_bands"] = parsed_data["header"][2]
            else:
                # hope no bands just materialize out of thin air
                assert result["n_bands"] == parsed_data["header"][2]
            # gather k-point quantities for each segment
            result["n_k"].append(parsed_data["header"][3])
            result["path"].append((tuple(parsed_data["k_path"][:3]), tuple(parsed_data["k_path"][3:])))
            bands.append(np.array(parsed_data["bands"].asList()).reshape(result["n_k"][-1], result["n_bands"]))
        result["bands"] = np.vstack(bands)
        return result
