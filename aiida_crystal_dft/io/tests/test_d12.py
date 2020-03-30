#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.


from aiida_crystal_dft.tests.fixtures import test_basis_family_predefined

def test_d12_formatter():
    from aiida_crystal_dft.io.d12 import D12Formatter
    formatter = D12Formatter()
    assert formatter.get_value_type(["geometry", "optimise", "type"]) == "string"
    assert formatter.get_value_type(["scf", "numerical", "BIPOSIZE"]) == "integer"


def test_input_full():
    from aiida_crystal_dft.tests import d12_input, d12_expected
    from aiida_crystal_dft.io.d12 import D12
    d12_file = D12(parameters=d12_input)
    outstr = str(d12_file)
    assert outstr == d12_expected
