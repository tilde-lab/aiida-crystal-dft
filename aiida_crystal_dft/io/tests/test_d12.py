#  Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.


from aiida_crystal_dft.tests.fixtures import test_basis_family_predefined, test_basis_family


def test_input_full(test_basis_family_predefined):
    from aiida_crystal_dft.tests import d12_input, d12_expected
    from aiida_crystal_dft.io.d12 import D12
    d12_file = D12(parameters=d12_input, basis=test_basis_family_predefined)
    outstr = str(d12_file)
    assert outstr == d12_expected
