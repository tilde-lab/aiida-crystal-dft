""" Base workflows for CRYSTAL code. These are meant to handle failures/restarts/etc...
"""

from aiida.orm import CalculationFactory
from aiida.orm.code import Code
from aiida.common.extendeddicts import AttributeDict
from aiida.work.workchain import WorkChain, append_
from aiida_crystal.aiida_compatibility import get_data_class
from aiida_crystal.data.basis_set import get_basissets_from_structure
from aiida_crystal.utils.kpoints import get_shrink_kpoints_path
from aiida_crystal.utils.dos import get_dos_projections_atoms


class BaseCrystalWorkChain(WorkChain):
    """Run CRYSTAL calculation"""

    _calculation = 'crystal.serial'

    @classmethod
    def define(cls, spec):
        super(BaseCrystalWorkChain, cls).define(spec)
        # define inputs
        spec.input('code', valid_type=Code)
        spec.input('structure', valid_type=get_data_class('structure'), required=True)
        spec.input('parameters', valid_type=get_data_class('parameter'), required=True)
        spec.input('basis_family', valid_type=get_data_class('str'))
        spec.input('options', valid_type=get_data_class('parameter'), required=True, help="Calculation options")
        # define workchain routine
        spec.outline(cls.init_calculation,
                     cls.run_calculation,
                     cls.retrieve_results)
        # define outputs
        spec.output('output_structure', valid_type=get_data_class('structure'), required=False)
        spec.output('primitive_structure', valid_type=get_data_class('structure'), required=False)
        spec.output('output_parameters', valid_type=get_data_class('parameter'), required=False)
        spec.output('output_wavefunction', valid_type=get_data_class('singlefile'), required=False)

    def init_calculation(self):
        """Create input dictionary for the calculation, deal with restart (later?)"""
        self.ctx.inputs = AttributeDict()
        # set the code
        self.ctx.inputs.code = self.inputs.code
        # set the (primitive?) structure
        self.ctx.inputs.structure = self.inputs.structure
        # set parameters
        self.ctx.inputs.parameters = self.inputs.parameters
        # set basis
        self.ctx.inputs.basis = get_basissets_from_structure(self.inputs.structure,
                                                             family_name=self.inputs.basis_family.value)
        # set settings
        if 'options' in self.inputs:
            self.ctx.inputs.options = self.inputs.options

    def run_calculation(self):
        """Run a calculation from self.ctx.inputs"""
        process = CalculationFactory(self._calculation).process()
        options = self.ctx.inputs.pop('options')
        running = self.submit(process, options=options.get_dict(), **self.ctx.inputs)
        return self.to_context(calculations=append_(running))

    def retrieve_results(self):
        """Process calculation results; adapted from aiida_vasp"""
        # return the results of the last calculation
        last_calc = self.ctx.calculations[-1]
        for name, port in self.spec().outputs.items():
            if port.required and name not in last_calc.out:
                self.report('the spec specifies the output {} as required '
                            'but was not an output of {}<{}>'.format(name, self._calculation.__name__,
                                                                     last_calc.pk))

            if name in last_calc.out:
                node = last_calc.out[name]
                self.out(name, last_calc.out[name])
                # self.report("attaching the node {}<{}> as '{}'".format(node.__class__.__name__, node.pk, name))
        return


class BasePropertiesWorkChain(WorkChain):
    """Run Properties calculation"""

    _calculation = 'crystal.properties'

    @classmethod
    def define(cls, spec):
        super(BasePropertiesWorkChain, cls).define(spec)
        # define inputs
        spec.input('code', valid_type=Code)
        spec.input('wavefunction', valid_type=get_data_class('singlefile'), required=True)
        spec.input('parameters', valid_type=get_data_class('parameter'), required=True)
        spec.input('options', valid_type=get_data_class('parameter'), required=True, help="Calculation options")
        # define workchain routine
        spec.outline(cls.init_calculation,
                     cls.run_calculation,
                     cls.retrieve_results)
        # define outputs
        spec.output('output_bands', valid_type=get_data_class('array.bands'), required=False)
        spec.output('output_dos', valid_type=get_data_class('array'), required=False)

    def init_calculation(self):
        """Create input dictionary for the calculation, deal with restart (later?)"""
        self.ctx.inputs = AttributeDict()
        # set the code
        self.ctx.inputs.code = self.inputs.code
        # set the wavefunction
        self.ctx.inputs.wavefunction = self.inputs.wavefunction
        # set parameters, giving the defaults
        self.ctx.inputs.parameters = self._set_default_parameters(self.inputs.parameters)
        # set options
        if 'options' in self.inputs:
            self.ctx.inputs.options = self.inputs.options

    def _set_default_parameters(self, parameters):
        """Set defaults to calculation parameters"""
        parameters_dict = parameters.get_dict()
        from aiida_crystal.io.f9 import Fort9
        wf = Fort9(self.inputs.wavefunction.get_file_abs_path())
        if 'band' in parameters_dict:
            # automatic generation of k-point path
            if 'bands' not in parameters_dict['band']:
                self.logger.info('Proceeding with automatic generation of k-points path')
                structure = wf.get_structure()
                shrink, points, path = get_shrink_kpoints_path(structure)
                parameters_dict['band']['shrink'] = shrink
                parameters_dict['band']['bands'] = path
            # automatic generation of first and last band
            if 'first' not in parameters_dict['band']:
                parameters_dict['band']['first'] = 1
            if 'last' not in parameters_dict['band']:
                parameters_dict['band']['last'] = wf.get_ao_number()

        if 'dos' in parameters_dict:
            # automatic generation of projections in case no projections are given
            # TODO: explicit asking for automatic projections
            if ('projections_atoms' not in parameters_dict['dos'] and
                    'projections_orbitals' not in parameters_dict['dos']):
                self.logger.info('Proceeding with automatic generation of dos atomic projections')
                parameters_dict['dos']['projections_atoms'] = get_dos_projections_atoms(wf.get_atomic_numbers())
            # automatic generation of first and last band
            if 'first' not in parameters_dict['dos']:
                parameters_dict['dos']['first'] = 1
            if 'last' not in parameters_dict['dos']:
                parameters_dict['dos']['last'] = wf.get_ao_number()
        return get_data_class('parameter')(dict=parameters_dict)

    def run_calculation(self):
        """Run a calculation from self.ctx.inputs"""
        process = CalculationFactory(self._calculation).process()
        options = self.ctx.inputs.pop('options')
        running = self.submit(process, options=options.get_dict(), **self.ctx.inputs)
        return self.to_context(calculations=append_(running))

    def retrieve_results(self):
        """Process calculation results; adapted from aiida_vasp"""
        # return the results of the last calculation
        last_calc = self.ctx.calculations[-1]
        for name, port in self.spec().outputs.items():
            if port.required and name not in last_calc.out:
                self.report('the spec specifies the output {} as required '
                            'but was not an output of {}<{}>'.format(name, self._calculation.__name__,
                                                                     last_calc.pk))

            if name in last_calc.out:
                node = last_calc.out[name]
                self.out(name, last_calc.out[name])
                # self.report("attaching the node {}<{}> as '{}'".format(node.__class__.__name__, node.pk, name))
        return
