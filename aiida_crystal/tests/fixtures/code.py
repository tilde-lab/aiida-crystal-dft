#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.


import pytest


@pytest.fixture
def test_computer(aiida_profile, new_workdir):
    from aiida.common.exceptions import NotExistent
    try:
        computer = aiida_profile._backend.computers.get(name='localhost')
    except NotExistent:
        computer = aiida_profile._backend.computers.create(
                name='localhost',
                description='localhost computer set up by aiida_crystal tests',
                hostname='localhost',
                workdir=new_workdir,
                transport_type='local',
                scheduler_type='direct',
                enabled_state=True)
    return computer


@pytest.fixture
def test_code(test_computer):
    from aiida.orm import Code
    if not test_computer.pk:
        test_computer.store()
    code = Code()
    code.label = 'crystal'
    code.description = 'CRYSTAL code'
    code.set_remote_computer_exec((test_computer, '/usr/local/bin/crystal'))
    code.set_input_plugin_name('crystal.main')
    return code
