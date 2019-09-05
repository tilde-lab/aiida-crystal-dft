#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import os
import shutil
import tempfile
import pytest
from ase.spacegroup import crystal


@pytest.fixture
def crystal_calc(test_crystal_code, crystal_calc_parameters, test_structure_data, test_basis_family_predefined):
    from aiida.common.extendeddicts import AttributeDict
    from aiida_crystal.calculations.serial import CrystalSerialCalculation
    inputs = AttributeDict()
    inputs.metadata = AttributeDict({'options':
                                         {'resources':
                                              {"num_machines": 1, "num_mpiprocs_per_machine": 1}
                                          }
                                     })
    inputs.code = test_crystal_code
    inputs.structure = test_structure_data
    inputs.parameters = crystal_calc_parameters
    inputs.basis_family = test_basis_family_predefined
    calc = CrystalSerialCalculation(inputs)
    return calc


@pytest.fixture
def crystal_calc_results(crystal_calc):
    from aiida.orm import FolderData
    from aiida_crystal.tests import TEST_DIR

    def get_results(prefix=None):
        if prefix is None:
            prefix = "mgo_sto3g"
        data = FolderData()
        data.put_object_from_tree(os.path.join(TEST_DIR, 'output_files', prefix))
        return data
    return get_results


@pytest.fixture
def crystal_calc_node(crystal_calc, crystal_calc_results):
    """Returns CalcJobNode corresponding to CrystalCalc CalcJob"""
    from aiida.orm import CalcJobNode, FolderData
    from aiida.common.links import LinkType
    computer = crystal_calc.inputs.code.get_remote_computer()
    process_type = 'aiida.calculations:{}'.format('crystal.serial')
    node = CalcJobNode(computer=computer, process_type=process_type)
    node.set_process_label('CrystalSerialCalculation')
    node.set_attribute('input_filename', 'INPUT')
    node.set_attribute('output_filename', '_scheduler-stderr.txt')
    node.set_attribute('error_filename', '_scheduler-stderr.txt')
    node.set_option('resources', {'num_machines': 1, 'num_mpiprocs_per_machine': 1})
    node.add_incoming(crystal_calc.inputs.code, link_type=LinkType.INPUT_CALC, link_label='code')
    node.add_incoming(crystal_calc.inputs.structure, link_type=LinkType.INPUT_CALC, link_label='structure')
    node.add_incoming(crystal_calc.inputs.parameters, link_type=LinkType.INPUT_CALC, link_label='parameters')
    node.add_incoming(crystal_calc.inputs.basis_family, link_type=LinkType.INPUT_CALC, link_label='basis_family')
    node.store()
    retrieved = crystal_calc_results()
    retrieved.add_incoming(node, link_type=LinkType.CREATE, link_label='retrieved')
    retrieved.store()
    return node


@pytest.fixture
def properties_calc(test_properties_code, properties_calc_parameters, test_wavefunction):
    from aiida.common.extendeddicts import AttributeDict
    from aiida_crystal.calculations.properties import PropertiesCalculation
    inputs = AttributeDict()
    inputs.metadata = AttributeDict({'options':
                                         {'resources':
                                              {"num_machines": 1, "num_mpiprocs_per_machine": 1}
                                          }
                                     })
    inputs.code = test_properties_code
    inputs.parameters = properties_calc_parameters
    inputs.wavefunction = test_wavefunction
    calc = PropertiesCalculation(inputs)
    return calc


@pytest.fixture
def properties_calc_results(properties_calc):
    from aiida.common.folders import SandboxFolder
    from aiida.orm.nodes.data.folder import FolderData
    from aiida_crystal.tests import TEST_DIR
    out_files = [os.path.join(TEST_DIR, "output_files", "mgo_sto3g_external.{}".format(f))
                 for f in properties_calc.retrieve_list]
    with SandboxFolder() as folder:
        for src, dst in zip(out_files, properties_calc.retrieve_list):
            shutil.copy(src, os.path.join(folder.abspath, dst))
        data = FolderData()
        data.replace_with_folder(folder.abspath)
        yield data


def properties_calc_node(properties_calc, properties_calc_results):
    """Returns CalcJobNode corresponding to PropertiesCalc CalcJob"""
    from aiida.orm import CalcJobNode
    from aiida.common.links import LinkType
    computer = properties_calc.inputs.code.get_remote_computer()
    process_type = 'aiida.calculations:{}'.format('properties')
    node = CalcJobNode(computer=computer, process_type=process_type)
    node.set_option('resources', {'num_machines': 1, 'num_mpiprocs_per_machine': 1})
    node.set_attribute('input_filename', 'INPUT')
    node.set_attribute('output_filename', '_scheduler-stderr.txt')
    node.set_attribute('error_filename', '_scheduler-stderr.txt')
    node.add_incoming(properties_calc.inputs.code, link_type=LinkType.INPUT_CALC, link_label='code')
    node.add_incoming(properties_calc.inputs.parameters, link_type=LinkType.INPUT_CALC, link_label='parameters')
    node.add_incoming(properties_calc.inputs.wavefunction, link_type=LinkType.INPUT_CALC, link_label='wavefunction')


@pytest.fixture
def crystal_calc_parameters():
    from aiida.orm import Dict
    return Dict(dict={
        "title": "Crystal calc",
        "scf": {
            "k_points": (8, 8)
        }
    })


@pytest.fixture
def properties_calc_parameters():
    from aiida.orm import Dict
    return Dict(dict={
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
    from aiida.orm import SinglefileData
    from aiida_crystal.tests import TEST_DIR
    file_name = os.path.join(TEST_DIR,
                             'output_files',
                             'mgo_sto3g_external.fort.9')
    temp_dir = tempfile.gettempdir()
    expected = os.path.join(temp_dir, "fort.9")
    shutil.copy(file_name, expected)
    with open(expected, 'rb') as f:
        yield SinglefileData(file=f)
    os.remove(expected)


@pytest.fixture
def test_ase_structure():
    # LiCl
    # return crystal(
    #     symbols=['Cl', 'Li'],
    #     basis=[[0.3333333333, 0.6666666667, 0.379], [0.3333333333, 0.6666666667, 0.0]],
    #     spacegroup=186,
    #     cellpar=[3.852, 3.852, 6.118, 90.0, 90.0, 120.0])
    # MgO
    return crystal(
        symbols=[12, 8],
        basis=[[0, 0, 0], [0.5, 0.5, 0.5]],
        spacegroup=225,
        cellpar=[4.21, 4.21, 4.21, 90, 90, 90])


@pytest.fixture
def test_structure_data(aiida_profile, test_ase_structure):
    from aiida.orm import StructureData
    return StructureData(ase=test_ase_structure)
