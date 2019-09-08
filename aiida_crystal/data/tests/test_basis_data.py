"""
Tests of BasisSetData
"""
import os
import pytest

from aiida_crystal.tests import TEST_DIR
import aiida_crystal.tests.utils as tests


# pylint: disable=unused-argument


def test_create_single(new_database, new_workdir):
    """A test creating single basis node"""

    from aiida.plugins import DataFactory

    basis = DataFactory("crystal.basisset")(
        file=os.path.join(TEST_DIR, "input_files", "sto3g", 'sto3g_Mg.basis'))

    expected_meta = {
        'num_shells': 3,
        'author': 'John Smith',
        'atomic_number': 12,
        'filename': 'sto3g_Mg.basis',
        'element': 'Mg',
        'year': 1999,
        'basis_type': 'all-electron',
        'class': 'sto3g',
        'md5': '0731ecc3339d2b8736e61add113d0c6f'
    }

    assert basis.metadata == expected_meta

    expected_content = """12 3
1 0 3  2.  0.
1 1 3  8.  0.
1 1 3  2.  0."""
    assert basis.content == expected_content

    basis.store()

    # try retrieving a pre-existing (stored) basis
    basis, created = DataFactory("crystal.basisset").get_or_create(
        filepath=os.path.join(TEST_DIR, "input_files", "sto3g",
                              'sto3g_Mg.basis'))
    assert not created


def test_create_group(new_database, new_workdir):
    """A test that creates basis group"""
    from aiida_crystal.data.basis_set import BasisSetData
    upload_basisset_family = BasisSetData.upload_basisset_family

    nfiles, nuploaded = upload_basisset_family(
        os.path.join(TEST_DIR, "input_files", "sto3g"), "sto3g",
        "group of sto3g basis sets")
    assert (nfiles, nuploaded) == (3, 3)

    nfiles, nuploaded = upload_basisset_family(
        os.path.join(TEST_DIR, "input_files", "311g_ae"), "311g",
        "group of 311g basis sets")
    assert (nfiles, nuploaded) == (3, 3)

    group = BasisSetData.get_basis_group("sto3g")
    assert group.description == "group of sto3g basis sets"

    groups = BasisSetData.get_basis_groups(filter_elements="O")
    assert len(groups) == 1

    # try uploading the files to a second group
    with pytest.raises(ValueError):
        upload_basisset_family(
            os.path.join(TEST_DIR, "input_files", "sto3g"),
            "another_sto3g",
            "another group of sto3g basis sets",
            stop_if_existing=True)

    nfiles, nuploaded = upload_basisset_family(
        os.path.join(TEST_DIR, "input_files", "sto3g"),
        "another_sto3g",
        "another group of sto3g basis sets",
        stop_if_existing=False)
    assert (nfiles, nuploaded) == (3, 0)


def test_bases_from_struct(new_database, new_workdir):
    """A test for creating basis files from struct"""

    from aiida_crystal.data.basis_set import BasisSetData
    upload_basisset_family = BasisSetData.upload_basisset_family

    _, _ = upload_basisset_family(
        os.path.join(TEST_DIR, "input_files", "sto3g"), "sto3g",
        "group of sto3g basis sets")

    # MgO
    from ase.spacegroup import crystal
    atoms = crystal(
        symbols=[12, 8],
        basis=[[0, 0, 0], [0.5, 0.5, 0.5]],
        spacegroup=225,
        cellpar=[4.21, 4.21, 4.21, 90, 90, 90])

    atoms[0].tag = 1
    atoms[1].tag = 1

    from aiida.plugins import DataFactory
    struct = DataFactory("structure")(ase=atoms)

    from aiida_crystal.data.basis_set import get_basissets_by_kind
    bases_dict = get_basissets_by_kind(struct, "sto3g")
    print(list(atoms))

    assert set(bases_dict.keys()) == {"Mg", "Mg1", "O"}
