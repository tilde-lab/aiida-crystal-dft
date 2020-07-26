#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A parser for fort.25 bands and DOS files
"""
import numpy as np
import pyparsing as pp

from aiida_crystal_dft.io import _parse_string

pc = pp.pyparsing_common

__all__ = ["Fort25"]


def band_parser():
    header = (pc.integer + pp.Word(pp.alphas) + 2 * pc.integer + 3 * pc.sci_real).setResultsName('header')
    e = (2 * pc.sci_real).setResultsName('energy')
    k_path = (6 * pc.signed_integer).setResultsName('path')
    bands = pp.OneOrMore(pc.sci_real).setResultsName('data')
    return header + e + k_path + bands


class Fort25(object):

    def __init__(self, file):
        """A collection of parsers for various parts of fort.25 file."""
        if isinstance(file, str):
            with open(file, 'r') as f:
                self._data = f.read().split('-%-')
        else:
            self._data = file.read().split('-%-')
        # parsers should be registered in the following dictionary
        self._parser = {
            "BAND": _parse_bands,
            "DOSS": _parse_dos,
        }

    def parse(self):
        """The main parsing function. Returns a dictionary"""
        result = {}
        # the resulting dictionary
        for part in self._parser.keys():
            data = [bloc for bloc in self._data if bloc[1:5] == part]
            if data:
                result[part] = self._parser[part](data)
        return result


def _parse_bands(data):
    """Band structure parser"""
    bands = []
    result = {
        "n_bands": 0,
        "n_k": [],
        "path": [],
        "bands": None
    }
    for datum in data:
        parsed_data = _parse_string(band_parser(), datum)
        if not result["n_bands"]:
            result["n_bands"] = parsed_data["header"][2]
        else:
            # hope no bands just materialize out of thin air
            assert result["n_bands"] == parsed_data["header"][2]
        # gather k-point quantities for each segment
        result["n_k"].append(parsed_data["header"][3])
        result["path"].append((tuple(parsed_data["path"][:3]), tuple(parsed_data["path"][3:])))
        bands.append(np.array(parsed_data["data"].asList()).reshape(result["n_k"][-1], result["n_bands"]))
    result["bands"] = np.vstack(bands)
    return result


def _parse_dos(data):
    """Density of states parser. The parser used is the same as for bands"""
    dos = []
    result = {
        "e_fermi": 0.,
        "e": None,
        "dos": None,
    }
    for datum in data:
        parsed_data = _parse_string(band_parser(), datum)
        _, _, _, n, de, _, e_fermi = parsed_data["header"]
        e0, _ = parsed_data["energy"]
        if result["e"] is None:
            result["e"] = np.linspace(e0, e0 + de * (n - 1), n)
            result["e_fermi"] = e_fermi
        else:
            assert (e0, de, n) == (result["e"][0], result["e"][1] - result["e"][0], len(result["e"]))
            assert result["e_fermi"] == e_fermi
        dos.append(np.array(parsed_data["data"].asList()))
    result["dos"] = np.vstack(dos)
    return result
