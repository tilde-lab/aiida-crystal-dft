"""
test d3 schema
"""
#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import pytest
from aiida_crystal.validation import validate_with_json
from jsonschema import ValidationError


@pytest.mark.parametrize("test_input", [{},
                                        {"a": 1},
                                        {"band": {}},
                                        {"band": {"shrink": 8}},
                                        {"band": {"shrink": 8,
                                                  "kpoints": 12,
                                                  "first": 7,
                                                  "last": 14,
                                                  "bands": [["G", "Q", "Y"]]}},
                                        ]
                         )
def test_toplevel_fail(test_input):
    with pytest.raises(ValidationError):
        validate_with_json({}, name='d3')
    with pytest.raises(ValidationError):
        validate_with_json({"a": 1}, name='d3')


def test_toplevel_pass():
    data = {
        "band": {
            "shrink": 12,
            "kpoints": 30,
            "first": 7,
            "last": 14,
            "bands": [["G", "Y"]]
        }
    }
    validate_with_json(data, name="d3")


def test_full_pass():
    data = {
        "band": {
            "title": "some title",
            "shrink": 12,
            "kpoints": 30,
            "first": 7,
            "last": 14,
            "bands": [[[0, 3, 6], [6, 6, 6]]],
            "store": True,
            "print": False
        }
    }
    validate_with_json(data, "d3")
