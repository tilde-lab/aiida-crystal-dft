#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
An adapter for writing out .d3 file (for properties calculation)
"""
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
        if self._parameters is None:
            raise ValueError("No ParameterData is given for .d3 input")
        if isinstance(self._parameters['band']['bands'][0][0], six.string_types):
            self._parameters['band']['shrink'] = 0

    def use_parameters(self, parameters):
        validate_with_json(parameters.get_dict(), name="d3")
        self._parameters = parameters.get_dict()

    def __str__(self):
        self._validate()
        lines = self._band_block_str()
        return "\n".join(lines)

    def _band_block_str(self):
        band = self._parameters.get("band", None)
        if band is None:
            return []
        lines = ["BAND",
                 "{}".format(band.get("title", "CRYSTAL RUN")),
                 "{} {} {} {} {} {}".format(len(band["bands"]),
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
