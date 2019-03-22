#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import os
import shutil
import tempfile
import pytest
from ase.spacegroup import crystal


@pytest.fixture
def crystal_calc(test_crystal_code, crystal_calc_parameters, test_structure_data, test_basis):
    from aiida_crystal.calculations.serial import CrystalSerialCalculation
    calc = CrystalSerialCalculation(resources={"num_machines": 1, "num_mpiprocs_per_machine": 1})
    calc.use_code(test_crystal_code)
    calc.set_computer(test_crystal_code.get_computer())
    calc.use_structure(test_structure_data)
    calc.use_parameters(crystal_calc_parameters)
    calc.use_basis(test_basis['Mg'], 'Mg')
    calc.use_basis(test_basis['O'], 'O')
    return calc


@pytest.fixture
def crystal_calc_results(crystal_calc):
    from aiida.common.folders import SandboxFolder
    from aiida.orm.data.folder import FolderData
    from aiida_crystal.tests import TEST_DIR
    out_files = [os.path.join(TEST_DIR, "output_files", "mgo_sto3g_external.{}".format(f))
                 for f in crystal_calc.retrieve_list]
    with SandboxFolder() as folder:
        for src, dst in zip(out_files, crystal_calc.retrieve_list):
            shutil.copy(src, os.path.join(folder.abspath, dst))
        data = FolderData()
        data.replace_with_folder(folder.abspath)
        yield data


@pytest.fixture
def properties_calc(test_properties_code, properties_calc_parameters, test_wavefunction):
    from aiida_crystal.calculations.properties import PropertiesCalculation
    calc = PropertiesCalculation(resources={"num_machines": 1, "num_mpiprocs_per_machine": 1})
    calc.use_code(test_properties_code)
    calc.set_computer(test_properties_code.get_computer())
    calc.use_parameters(properties_calc_parameters)
    calc.use_wavefunction(test_wavefunction)
    return calc


@pytest.fixture
def properties_calc_results(properties_calc):
    from aiida.common.folders import SandboxFolder
    from aiida.orm.data.folder import FolderData
    from aiida_crystal.tests import TEST_DIR
    out_files = [os.path.join(TEST_DIR, "output_files", "mgo_sto3g_external.{}".format(f))
                 for f in properties_calc.retrieve_list]
    with SandboxFolder() as folder:
        for src, dst in zip(out_files, properties_calc.retrieve_list):
            shutil.copy(src, os.path.join(folder.abspath, dst))
        data = FolderData()
        data.replace_with_folder(folder.abspath)
        yield data


@pytest.fixture
def crystal_calc_parameters():
    from aiida.orm.data.parameter import ParameterData
    return ParameterData(dict={
        "title": "MgO Bulk",
        "scf": {
            "k_points": (8, 8)
        }
    })


@pytest.fixture
def properties_calc_parameters():
    from aiida.orm.data.parameter import ParameterData
    return ParameterData(dict={
        "band": {
            "shrink": 8,
            "k_points": 30,
            "first": 1,
            "last": 14,
            "bands": [[[0, 0, 0], [4, 0, 4]],
                      [[4, 0, 4], [5, 2, 5]],
                      [[3, 3, 6], [0, 0, 0]],
                      [[0, 0, 0], [4, 4, 4]],
                      [[4, 4, 4], [4, 2, 6]],
                      [[4, 2, 6], [4, 0, 4]]]
        }
    })

@pytest.fixture
def test_wavefunction():
    from aiida.orm.data.singlefile import SinglefileData
    from aiida_crystal.tests import TEST_DIR
    file_name = os.path.join(TEST_DIR,
                             'output_files',
                             'mgo_sto3g_external.fort.9')
    temp_dir = tempfile.gettempdir()
    expected = os.path.join(temp_dir, "fort.9")
    shutil.copy(file_name, expected)
    yield SinglefileData(file=expected)
    os.remove(expected)


@pytest.fixture
def test_ase_structure():
    # MgO
    return crystal(
        symbols=[12, 8],
        basis=[[0, 0, 0], [0.5, 0.5, 0.5]],
        spacegroup=225,
        cellpar=[4.21, 4.21, 4.21, 90, 90, 90])


@pytest.fixture
def test_structure_data(aiida_profile, test_ase_structure):
    from aiida.orm.data.structure import StructureData
    return StructureData(ase=test_ase_structure)
