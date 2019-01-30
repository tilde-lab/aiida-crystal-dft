"""A test for CRYSTAL immigrant calculation"""

import os
import shutil

from aiida_crystal.tests import TEST_DIR
import aiida_crystal.tests.utils as tests


def get_main_code(workdir):
    """get the crystal.basic code """
    computer = tests.get_computer(workdir=workdir)
    # get code
    code = tests.get_code(entry_point='crystal.main', computer=computer)

    return code


def test_full(new_database, new_workdir):
    """ Test CRYSTAL immigrant calculation
    :param new_database: a test database
    :param new_workdir: working directory """
    from aiida_crystal.calculations.cry_main_immigrant import CryMainImmigrantCalculation

    computer = tests.get_computer(workdir=new_workdir, configure=True)
    code = tests.get_code(entry_point='crystal.main', computer=computer)

    inpath = os.path.join(TEST_DIR, "input_files", 'nio_sto3g_afm.crystal.d12')
    outpath = os.path.join(TEST_DIR, "output_files",
                           'nio_sto3g_afm.crystal.out')

    shutil.copy(inpath, new_workdir)
    shutil.copy(outpath, new_workdir)

    resources = {'num_machines': 1, 'num_mpiprocs_per_machine': 16}

    calc = CryMainImmigrantCalculation(
        computer=computer,
        resources=resources,
        remote_workdir=new_workdir,
        input_file_name='nio_sto3g_afm.crystal.d12',
        output_file_name='nio_sto3g_afm.crystal.out')
    calc.use_code(code)

    transport = computer.get_transport()

    with transport as open_transport:
        calc.create_input_nodes(open_transport)
        calc.prepare_for_retrieval_and_parsing(open_transport)

    assert set(calc.get_inputs_dict().keys()) == {'basis_O', 'parameters', 'settings', 'basis_Ni', 'code', 'structure'}

    # TODO block until parsed, then test outputs (requires workflow?)
    # print(calc.get_outputs_dict())
    # print(calc.has_finished())
    # print(calc.has_finished_ok())
    # print(calc.get_state())
    # print(calc.get_scheduler_error())
    # print(calc.get_scheduler_output())
    # from aiida.backends.utils import get_log_messages
    # print(get_log_messages(calc))
