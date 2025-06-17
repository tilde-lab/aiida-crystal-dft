#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import os
import shutil
import tempfile
import pytest
from ase.spacegroup import crystal


@pytest.fixture
def crystal_calc_inputs(mock_crystal_code, crystal_calc_parameters, test_structure_data, test_basis_family_predefined):
    from aiida.common.extendeddicts import AttributeDict
    from aiida.orm import Bool

    inputs = AttributeDict()
    inputs.metadata = AttributeDict({
        'options': {
            'resources': {
                "num_machines": 1,
                "num_mpiprocs_per_machine": 1
            }
        }
    })
    inputs.code = mock_crystal_code
    inputs.structure = test_structure_data
    inputs.parameters = crystal_calc_parameters
    inputs.basis_family = test_basis_family_predefined
    inputs.guess_oxistates = Bool(False)
    inputs.high_spin_preferred = Bool(False)
    inputs.is_magnetic = Bool(True)
    return inputs


@pytest.fixture
def calc_results():
    from aiida.orm import FolderData
    from aiida_crystal_dft.tests import TEST_DIR

    def get_results(files=None, prefix="mgo_sto3g"):
        """
        Return a FolderData with the results of the calculation
        :param files: a dictionary corresponding files to directories
        :param prefix: a folder with all output files for the test calculation
        :return: a FolderData instance
        """
        data = FolderData()
        if files is None:
            files = {}
        # copy files from prefix
        root_dir = os.path.join(TEST_DIR, 'output_files', prefix)
        for entry in os.listdir(root_dir):
            if os.path.isfile(os.path.join(root_dir, entry)):
                # non-default file location
                if entry in files:
                    file_dir = os.path.join(TEST_DIR, 'output_files', files[entry])
                    with open(os.path.join(file_dir, entry), 'rb') as f:
                        data.put_object_from_filelike(f, entry)
                    continue
                # default file location
                with open(os.path.join(root_dir, entry), 'rb') as f:
                    data.put_object_from_filelike(f, entry)
        return data

    return get_results


@pytest.fixture
def crystal_calc_node(aiida_localhost, crystal_calc_inputs, calc_results):
    """Returns CalcJobNode corresponding to CrystalCalc CalcJob"""
    from aiida.orm import CalcJobNode, Dict,  StructureData
    from aiida.common.links import LinkType

    def get_calcnode(files=None, prefix="mgo_sto3g"):
        process_type = 'aiida.calculations:{}'.format('crystal_dft.serial')
        node = CalcJobNode(computer=aiida_localhost, process_type=process_type)
        node.set_process_label('CrystalSerialCalculation')
        node.base.attributes.set('input_filename', 'INPUT')
        node.base.attributes.set('output_filename', 'crystal.out')
        node.set_option('resources', {'num_machines': 1, 'num_mpiprocs_per_machine': 1})
        node.add_incoming(crystal_calc_inputs.code, link_type=LinkType.INPUT_CALC, link_label='code')
        # store inputs
        for calc_input in ("structure", "parameters", "basis_family"):
            crystal_calc_inputs[calc_input].store()
        # add incoming nodes
        node.add_incoming(crystal_calc_inputs.structure, link_type=LinkType.INPUT_CALC, link_label='structure')
        node.add_incoming(crystal_calc_inputs.parameters, link_type=LinkType.INPUT_CALC, link_label='parameters')
        node.add_incoming(crystal_calc_inputs.basis_family, link_type=LinkType.INPUT_CALC, link_label='basis_family')
        node.store()
        retrieved = calc_results(files, prefix)
        retrieved.add_incoming(node, link_type=LinkType.CREATE, link_label='retrieved')
        retrieved.store()
        return node

    return get_calcnode


@pytest.fixture
def properties_calc_inputs(mock_properties_code, properties_calc_parameters, test_wavefunction):
    from aiida.common.extendeddicts import AttributeDict
    inputs = AttributeDict()
    inputs.metadata = AttributeDict({'options':
                                     {'resources':
                                      {"num_machines": 1, "num_mpiprocs_per_machine": 1}
                                      }
                                     })
    inputs.code = mock_properties_code
    inputs.parameters = properties_calc_parameters
    inputs.wavefunction = test_wavefunction
    return inputs


@pytest.fixture
def properties_calc_node(aiida_localhost, properties_calc_inputs, calc_results):
    """Returns CalcJobNode corresponding to PropertiesCalc CalcJob"""
    from aiida.orm import CalcJobNode
    from aiida.common.links import LinkType
    process_type = 'aiida.calculations:{}'.format('crystal_dft.properties')

    def get_calcnode(files=None):
        node = CalcJobNode(computer=aiida_localhost, process_type=process_type)
        node.set_process_label('PropertiesCalculation')
        node.set_option('resources', {'num_machines': 1, 'num_mpiprocs_per_machine': 1})
        node.base.attributes.set('input_filename', 'INPUT')
        node.base.attributes.set('output_filename', '_scheduler-stderr.txt')
        node.base.attributes.set('error_filename', '_scheduler-stderr.txt')
        # store inputs
        for calc_input in ("parameters", "wavefunction"):
            properties_calc_inputs[calc_input].store()
        # add incoming nodes
        node.add_incoming(properties_calc_inputs.code, link_type=LinkType.INPUT_CALC, link_label='code')
        node.add_incoming(properties_calc_inputs.parameters, link_type=LinkType.INPUT_CALC, link_label='parameters')
        node.add_incoming(properties_calc_inputs.wavefunction, link_type=LinkType.INPUT_CALC, link_label='wavefunction')
        node.store()
        retrieved = calc_results(files)
        retrieved.add_incoming(node, link_type=LinkType.CREATE, link_label='retrieved')
        retrieved.store()
        return node

    return get_calcnode


@pytest.fixture
def crystal_calc_parameters():
    from aiida.orm import Dict
    return Dict(dict={
        "label": "Crystal calc",
        "scf": {
            "k_points": (8, 8),
            # 'dft': {'xc': 'PBE0'}
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
    from aiida_crystal_dft.tests import TEST_DIR
    file_name = os.path.join(TEST_DIR,
                             'output_files',
                             'mgo_sto3g',
                             'fort.9')
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
        # symbols=[26, 8],
        basis=[[0, 0, 0], [0.5, 0.5, 0.5]],
        spacegroup=225,
        cellpar=[4.21, 4.21, 4.21, 90, 90, 90])


@pytest.fixture
def test_mpds_structure(aiida_profile):
    from aiida.tools.dbimporters.plugins.mpds import MpdsDbImporter
    from aiida.orm import StructureData
    importer = MpdsDbImporter()
    query = {'formulae': 'HgEr', 'sgs': 221}
    res = next(importer.find(query))
    ase_struct = crystal(
        symbols=res['els_noneq'],
        basis=res['basis_noneq'],
        spacegroup=res['sg_n'],
        cellpar=res['cell_abc'])
    return StructureData(ase=ase_struct)


@pytest.fixture
def test_magnetic_structure(aiida_profile):
    from aiida.orm import StructureData
    ase_struct = crystal(
        symbols=[26, 8],
        basis=[[0, 0, 0], [0.5, 0.5, 0.5]],
        spacegroup=225,
        cellpar=[4.21, 4.21, 4.21, 90, 90, 90])
    return StructureData(ase=ase_struct)


@pytest.fixture
def test_structure_data(aiida_profile, test_ase_structure):
    from aiida.orm import StructureData
    return StructureData(ase=test_ase_structure)


@pytest.fixture
def test_structure_issue_30(aiida_profile):
    from .. import TEST_DIR
    # from aiida_crystal_dft.io.f9 import Fort9
    from aiida_crystal_dft.io.f34 import Fort34
    name = os.path.join(TEST_DIR,
                        "input_files",
                        "issue_30",
                        "fort.34")
    # parser = Fort9(name)
    struct = Fort34().read(name)
    print(struct.space_group)
    return struct.to_aiida()
