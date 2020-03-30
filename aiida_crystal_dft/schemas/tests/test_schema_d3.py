"""
test d3 schema
"""
#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import pytest
from aiida_crystal_dft.schemas import validate_with_json
from jsonschema import ValidationError


@pytest.mark.parametrize("test_input", [{},
                                        {"a": 1},
                                        {"band": {}},
                                        {"band": {"shrink": 8}},
                                        {"band": {"shrink": 8,
                                                  "k_points": 12,
                                                  "first": 7,
                                                  "last": 14,
                                                  "bands": [["G", "Q", "Y"]]}},
                                        {"newk": {}},
                                        {"newk": {"k_points": 8}},
                                        {"dos": {"n_e": 100,
                                                 "first": 7,
                                                 "last": 14,
                                                 "projections_atoms": 1}},
                                        ]
                         )
def test_band_toplevel_fail(test_input):
    with pytest.raises(ValidationError):
        validate_with_json(test_input, name='d3')


def test_toplevel_pass():
    data = {
        "band": {
            "shrink": 12,
            "k_points": 30,
            "first": 7,
            "last": 14,
            "bands": [["G", "Y"]]
        },
        "newk": {
            "k_points": [8, 8],
            "fermi": False,
        },
        "dos": {
            "n_e": 100,
            "first": 5,
            "last": 10,
            "projections_atoms": [[1], [2]]
        }
    }
    validate_with_json(data, name="d3")


def test_full_pass():
    data = {
        "band": {
            "title": "some title",
            "shrink": 12,
            "k_points": 30,
            "first": 7,
            "last": 14,
            "bands": [[[0, 3, 6], [6, 6, 6]]],
            "store": True,
            "print": False
        }
    }
    validate_with_json(data, "d3")
