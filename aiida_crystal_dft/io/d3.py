#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
An adapter for writing out .d3 file (for properties calculation)
"""
from __future__ import print_function

import pyparsing as pp
from collections import defaultdict
from aiida_crystal_dft.validation import validate_with_json
from aiida_crystal_dft.utils.keywords import PROPERTIES_KEYWORDS


pc = pp.pyparsing_common

def _band_parser():
    kw = pp.Keyword("BAND")
    title = pp.Word(pp.alphas)('title')
    settings = pp.Group(7 * pc.integer)('settings')
    point = pp.Group(3 * pc.integer)
    segment = pp.Group(2 * point)
    return kw + title + settings + pp.OneOrMore(segment)('path')


class D3(object):
    """A writer for .d3 file (input for properties calculation)"""

    def __init__(self, parameters=None):
        self._parameters = {}
        if parameters is not None:
            self.use_parameters(parameters)

    def read(self, file_name):
        """Read .d3 parameters from file"""
        if self._parameters:
            raise ValueError("Attempting to read parameters to not empty D3 instance!")
        with open(file_name) as f:
            lines = f.readlines()
        data = defaultdict(list)
        kw = ""
        for line in lines:
            if line.strip() in PROPERTIES_KEYWORDS:
                kw = line.strip()
            data[kw].append(line)
        bands = _band_parser().parseString(''.join(data['BAND']))
        return {'band':
            {
                'title': bands['title'],
                'shrink': bands['settings'][1]
            }
        }

    def _validate(self):
        """Scientific validation routine"""
        if self._parameters is None:
            raise ValueError("No ParameterData is given for .d3 input")
        if 'band' in self._parameters:
            if isinstance(self._parameters['band']['bands'][0][0], str):
                self._parameters['band']['shrink'] = 0

        if 'dos' in self._parameters and 'projections_atoms' not in self._parameters['dos']:
            self._parameters['dos']['projections_atoms'] = []
        if 'dos' in self._parameters and 'projections_orbitals' not in self._parameters['dos']:
            self._parameters['dos']['projections_orbitals'] = []

    def use_parameters(self, parameters):
        validate_with_json(parameters, name="d3")
        self._parameters = parameters

    def __str__(self):
        self._validate()
        lines = self._band_block_str()
        lines += self._newk_block_str()
        lines += self._dos_block_str()
        lines.append("END")
        return u"\n".join(lines)

    def write(self, f):
        """Writes the content to file f"""
        print(str(self), file=f)

    def _band_block_str(self):
        band = self._parameters.get("band", None)
        if band is None:
            return []
        lines = [
            "BAND",
            "{}".format(band.get("title", "CRYSTAL RUN")),
            "{} {} {} {} {} {} {}".format(len(band["bands"]),
                                          band["shrink"],
                                          band["k_points"],
                                          band["first"],
                                          band["last"],
                                          int(band.get("store", True)),
                                          int(band.get("write", False)))
        ]
        # now add lines to be explored
        if isinstance(band["bands"][0][0], str):
            format_line = '{0[0]}  {0[1]}'
        else:
            format_line = '{0[0][0]} {0[0][1]} {0[0][2]}  {0[1][0]} {0[1][1]} {0[1][2]}'
        lines += [format_line.format(line) for line in band["bands"]]
        return lines

    def _newk_block_str(self):
        newk = self._parameters.get("newk", None)
        if newk is None:
            return []
        lines = [
            "NEWK",
            "{0[0]} {0[1]}".format(newk["k_points"]),
            "{} {}".format(int(newk.get("fermi", True)), 0)  # 0 is the default for NPR
        ]
        return lines

    def _dos_block_str(self):
        dos = self._parameters.get("dos", None)
        if dos is None:
            return []
        lines = [
            "DOSS",
            "{} {} {} {} {} {} {}".format(len(dos["projections_atoms"]) + len(dos["projections_orbitals"]),
                                          dos["n_e"],
                                          dos["first"],
                                          dos["last"],
                                          dos.get("store", 1),
                                          dos.get("n_poly", 16),
                                          int(dos.get("print", False))
                                          ),
        ]
        lines += [("{} " * (len(proj_i) + 1)).format(-1 * len(proj_i), *proj_i) for proj_i in dos["projections_atoms"]]
        lines += [("{} " * (len(proj_i) + 1)).format(len(proj_i), *proj_i) for proj_i in dos["projections_orbitals"]]
        return lines
