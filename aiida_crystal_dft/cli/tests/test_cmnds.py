"""Tests of command line interface"""

import os
from click.testing import CliRunner
from aiida_crystal_dft.cli.basis import basis_set
from aiida_crystal_dft.tests import TEST_DIR


def test_predefined_basis_family(aiida_profile_clean):
    runner = CliRunner()
    result1 = runner.invoke(basis_set, ['createpredefined'])
    assert 'STO-6G' in result1.output
    assert 'POB-DZVP' in result1.output
    assert 'POB-DZVPP' in result1.output
    assert 'POB-TZVP' in result1.output
    result2 = runner.invoke(basis_set, ['createpredefined'])
    assert 'Created 0 predefined basis families' in result2.output


def test_upload_to_basis_family(aiida_profile):
    path = os.path.join(TEST_DIR, "input_files", "311g")
    runner = CliRunner()
    result1 = runner.invoke(basis_set, [
        'uploadfamily', '--path', path, '--name', 'TEST'])
    assert result1.exit_code == 0
    result2 = runner.invoke(basis_set, [
        'listfamilies'])
    assert "TEST" in result2.stdout
    result3 = runner.invoke(basis_set, [
        'listfamilies', '-e', 'Ag'])
    assert "TEST" in result3.stdout
    result4 = runner.invoke(basis_set, [
        'listfamilies', '-e', 'U'])
    assert "No Basis Set family contains all given elements and symbols" in result4.stdout
