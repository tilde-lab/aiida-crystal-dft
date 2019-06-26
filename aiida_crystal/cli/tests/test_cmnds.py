"""Tests of command line interface"""

import os
from click.testing import CliRunner
from aiida_crystal.cli.basis_set import basis_set
from aiida_crystal.tests import TEST_DIR


def test_basis_show(new_database):

    from aiida.orm import DataFactory
    basis_cls = DataFactory('crystal.basisset')
    node, created = basis_cls.get_or_create(
        os.path.join(TEST_DIR, "input_files", "sto3g", 'sto3g_O.basis'))

    runner = CliRunner()
    result = runner.invoke(basis_set, ['show', str(node.pk)])

    assert result.exit_code == 0

    expected = """atomic_number: 8
author:        John Smith
basis_type:    all-electron
class:         sto3g
element:       O
filename:      sto3g_O.basis
md5:           73a9c7315dc6edf6ab8bd4427a66f31c
num_shells:    2
year:          1999
"""

    assert expected in result.output

    result2 = runner.invoke(basis_set, ['show', '-c', str(node.pk)])

    assert result2.exit_code == 0


def test_basis_upload(new_database):

    path = os.path.join(TEST_DIR, "input_files", "sto3g")
    runner = CliRunner()
    result = runner.invoke(basis_set, [
        'uploadfamily', '--path', path, '--name', 'sto3g', '--description',
        'STO3G'
    ])

    assert result.exit_code == 0

    result2 = runner.invoke(basis_set, ['listfamilies', '-d'])

    assert result2.exit_code == 0

    assert 'sto3g' in result2.output
