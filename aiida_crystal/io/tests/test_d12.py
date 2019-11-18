#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.


def test_d12_formatter():
    from aiida_crystal.io.d12 import D12Formatter
    formatter = D12Formatter()
    assert formatter.get_value_type(["geometry", "optimise", "type"]) == "string"
    assert formatter.get_value_type(["scf", "numerical", "BIPOSIZE"]) == "integer"
