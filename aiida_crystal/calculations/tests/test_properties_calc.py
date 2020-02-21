#   Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_store_calc(properties_calc_node):
    calc = properties_calc_node()
    calc.store()
    assert calc.pk is not None
    assert calc.inputs.code.pk is not None
    assert calc.inputs.parameters.pk is not None
    assert calc.inputs.wavefunction.pk is not None


def test_validate_input(test_properties_code, properties_calc_parameters, test_wavefunction):
    from aiida.common.extendeddicts import AttributeDict
    from aiida_crystal.calculations.properties import PropertiesCalculation
    inputs = AttributeDict()
    with pytest.raises(ValueError):
        PropertiesCalculation(inputs)
    inputs.metadata = {'options': {'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1}}}
    inputs.code = test_properties_code
    with pytest.raises(ValueError):
        PropertiesCalculation(inputs)
    inputs.wavefunction = test_wavefunction
    with pytest.raises(ValueError):
        PropertiesCalculation(inputs)
    inputs.parameters = properties_calc_parameters
    assert PropertiesCalculation(inputs)


def test_submit(properties_calc):
    from aiida.common.folders import SandboxFolder
    with SandboxFolder() as folder:
        calcinfo = properties_calc.prepare_for_submission(folder=folder)
        assert properties_calc._PROPERTIES_FILE_NAME in calcinfo['retrieve_list']
        assert properties_calc._WAVEFUNCTION_FILE_NAME in folder.get_content_list()
        assert properties_calc._INPUT_FILE_NAME in folder.get_content_list()
        with folder.open(properties_calc._INPUT_FILE_NAME) as f:
            d3_content = f.read()
    assert d3_content == """BAND
CRYSTAL RUN
6 8 30 1 14 1 0
0 0 0  4 0 4
4 0 4  5 2 5
3 3 6  0 0 0
0 0 0  4 4 4
4 4 4  4 2 6
4 2 6  4 0 4
END
"""