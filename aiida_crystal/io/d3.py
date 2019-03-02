#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
An adapter for writing out .d3 file (for properties calculation)
"""
from __future__ import print_function
import six
from aiida_crystal.validation import validate_with_json


class D3(object):
    """A writer for .d3 file (input for properties calculation)"""

    def __init__(self, parameters=None):
        self._parameters = None
        if parameters is not None:
            self.use_parameters(parameters)

    def _validate(self):
        """Scientific validation routine"""
        from aiida.common.exceptions import ValidationError
        if self._parameters is None:
            raise ValueError("No ParameterData is given for .d3 input")
        if ("band" in self._parameters) and isinstance(self._parameters['band']['bands'][0][0], six.string_types):
            self._parameters['band']['shrink'] = 0
        dos = self._parameters.get("dos", {})
        if dos and "newk" not in self._parameters:
            raise ValidationError("NEWK must be set for DOS calculation")
        if dos and abs(dos["first"]) > abs(dos["last"]):
            raise ValidationError("DOS input: first band must be below last")

    def use_parameters(self, parameters):
        validate_with_json(parameters, name="d3")
        self._parameters = parameters

    def __str__(self):
        self._validate()
        lines = self._band_block_str()
        lines += self._newk_block_str()
        lines += self._dos_block_str()
        lines.append("END")
        return "\n".join(lines)

    def write(self, f):
        """Writes the content to file f"""
        print(self, file=f)

    def _band_block_str(self):
        band = self._parameters.get("band", None)
        if band is None:
            return []
        lines = [
            "BAND",
            "{}".format(band.get("title", "CRYSTAL RUN")),
            "{} {} {} {} {} {} {}".format(len(band["bands"]),
                                          band["shrink"],
                                          band["kpoints"],
                                          band["first"],
                                          band["last"],
                                          int(band.get("store", True)),
                                          int(band.get("write", False)))
        ]
        # now add lines to be explored
        if isinstance(band["bands"][0][0], six.string_types):
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
            "{0[0]} {0[1]}".format(newk["kpoints"]),
            "{} {}".format(int(newk.get("fermi", True)), 0)  # 0 is the default for NPR
        ]
        return lines

    def _dos_block_str(self):
        dos = self._parameters.get("dos", None)
        if dos is None:
            return []
        n_proj_at = len(dos["projections_atoms"]) if "projections_atoms" in dos else 0
        n_proj_ao = len(dos["projections_orbitals"]) if "projections_orbitals" in dos else 0
        lines = [
            "DOSS",
            "{} {} {} {} {} {} {}".format(n_proj_ao + n_proj_at,
                                          dos["n_e"],
                                          dos["first"],
                                          dos["last"],
                                          dos.get("store", 1),
                                          dos.get("n_poly", 16),
                                          int(dos.get("print", False))
                                          ),
        ]
        if n_proj_at:
            lines += [("{} " * (len(proj_i) + 1)).format(-1 * len(proj_i), *proj_i) for proj_i in
                      dos["projections_atoms"]]
        if n_proj_ao:
            lines += [("{} " * (len(proj_i) + 1)).format(len(proj_i), *proj_i) for proj_i in
                      dos["projections_orbitals"]]
        return lines
