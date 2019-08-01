#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.


import pytest


@pytest.fixture
def test_computer(aiida_profile, new_workdir):
    from aiida.orm import Computer
    from aiida.common import NotExistent
    try:
        computer = Computer.objects.get(name='localhost')
    except NotExistent:
        computer = Computer(
                name='localhost',
                description='localhost computer set up by aiida_crystal tests',
                hostname='localhost',
                workdir=new_workdir,
                transport_type='local',
                scheduler_type='direct')
    return computer


@pytest.fixture
def test_crystal_code(test_computer):
    from aiida.orm import Code
    if not test_computer.pk:
        test_computer.store()
    code = Code()
    code.label = 'crystal'
    code.description = 'CRYSTAL code'
    code.set_remote_computer_exec((test_computer, '/usr/local/bin/crystal'))
    code.set_input_plugin_name('crystal.serial')
    return code


@pytest.fixture
def test_properties_code(test_computer):
    from aiida.orm import Code
    if not test_computer.pk:
        test_computer.store()
    code = Code()
    code.label = 'properties'
    code.description = 'CRYSTAL properties code'
    code.set_remote_computer_exec((test_computer, '/usr/local/bin/properties'))
    code.set_input_plugin_name('crystal.properties')
    return code
