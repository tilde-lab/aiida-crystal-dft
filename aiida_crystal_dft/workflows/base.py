""" Base workflows for the CRYSTAL code. Handles the failures, restarts, etc.
"""

from aiida.plugins import CalculationFactory
from aiida.orm import Code, Bool, Dict, Int
from aiida.common.extendeddicts import AttributeDict
from aiida.engine import WorkChain, append_, while_
from aiida_crystal_dft.utils import get_data_node, get_data_class, not_
from aiida_crystal_dft.utils.kpoints import get_shrink_kpoints_path
from aiida_crystal_dft.utils.dos import get_dos_projections_atoms


DEFAULT_TITLE = 'CRYSTAL run by AiiDA'


class BaseCrystalWorkChain(WorkChain):
    """Run CRYSTAL calculation"""

    _serial_calculation = 'crystal_dft.serial'
    _parallel_calculation = 'crystal_dft.parallel'
    _number_restarts = 1

    @classmethod
    def define(cls, spec):
        super(BaseCrystalWorkChain, cls).define(spec)

        # define inputs
        spec.input('code', valid_type=Code)
        spec.input('structure', valid_type=get_data_class('structure'), required=True)
        spec.input('parameters', valid_type=get_data_class('dict'), required=True)
        spec.input('basis_family', valid_type=get_data_class('crystal_dft.basis_family'), required=True)
        spec.input('clean_workdir', valid_type=get_data_class('bool'),
                   required=False, default=lambda: get_data_node('bool', False))
        spec.input('options', valid_type=get_data_class('dict'), required=True, help="Calculation options")

        # define workchain routine
        spec.outline(cls.init_inputs,
                     while_(not_(cls._converged))(
                        cls.init_calculation,
                        cls.run_calculation,
                     ),
                     cls.retrieve_results,
                     cls.finalize)

        # define outputs
        spec.output('output_structure', valid_type=get_data_class('structure'), required=False)
        spec.output('primitive_structure', valid_type=get_data_class('structure'), required=False)
        spec.output('output_parameters', valid_type=get_data_class('dict'), required=False)
        spec.output('output_wavefunction', valid_type=get_data_class('singlefile'), required=False)
        spec.output('output_trajectory', valid_type=get_data_class('array.trajectory'), required=False)
        spec.output('oxidation_states', valid_type=get_data_class('dict'), required=False)

        # define error codes
        spec.exit_code(300, 'ERROR_CRYSTAL', message='CRYSTAL error')
        spec.exit_code(400, 'ERROR_UNKNOWN', message='Unknown error')

    def init_inputs(self):
        self.ctx.running_calc = 0

        # prepare inputs
        self.ctx.inputs = AttributeDict()
        self.ctx.inputs.code = self.inputs.code
        self.ctx.inputs.parameters = self.inputs.parameters
        self.ctx.inputs.basis_family = self.inputs.basis_family
        label = self.inputs.metadata.get('label', DEFAULT_TITLE)

        # work with options
        options_dict = self.inputs.options.get_dict()

        # oxidation states
        self.ctx.try_oxi = options_dict.pop('try_oxi_if_fails', False)
        use_oxi = options_dict.pop('use_oxidation_states', None)
        if use_oxi is not None:
            self.report(f'{label}: Using oxidation states: {use_oxi}')
            self.ctx.inputs.use_oxistates = Dict(dict=use_oxi)
        self.ctx.high_spin_preferred = options_dict.pop('high_spin_preferred', False)

        # magnetism
        is_magnetic = options_dict.pop('is_magnetic', False)
        if is_magnetic:
            self.report(f'{label}: is_magnetic is set, guessing magnetism')
            self.ctx.inputs.is_magnetic = Bool(True)
            self.ctx.inputs.spinlock_steps = Int(options_dict.pop('spinlock_steps', 5))

        # get calculation entry_point
        try:
            self.ctx.calculation = self._parallel_calculation \
                if (options_dict['resources']['num_machines'] > 1
                    or options_dict['resources']['num_mpiprocs_per_machine'] > 1) else self._serial_calculation
        except KeyError:
            self.ctx.calculation = self._parallel_calculation

        # remaining options are passed down to calculations
        self.ctx.options = options_dict

    def init_calculation(self):
        """Create input dictionary for the calculation, deal with restart (later?)"""
        # count number of previous calculations
        self.ctx.running_calc += 1

        # set the structure
        self.ctx.inputs.structure = self.inputs.structure

        # deal with oxidation states
        if self.ctx.running_calc > 1 and self.ctx.try_oxi:
            self.report('Trying to guess oxidation states')
            self.ctx.inputs.guess_oxistates = Bool(True)
            self.ctx.inputs.high_spin_preferred = Bool(self.ctx.high_spin_preferred)

        # set metadata
        label = self.inputs.metadata.get('label', DEFAULT_TITLE)
        description = self.inputs.metadata.get('description', '')
        self.ctx.inputs.metadata = AttributeDict({'options': self.ctx.options,
                                                  'label': '{} [{}]'.format(label, self.ctx.running_calc),
                                                  'description': description})

    def not_converged(self):
        return not self._converged()

    def _converged(self):
        """Check if calculation has converged"""
        if "calculations" not in self.ctx:
            return False  # if no calculations have run
        return self.ctx.calculations[-1].exit_status == 0 or self.ctx.running_calc == self._number_restarts

    def run_calculation(self):
        """Run a calculation from self.ctx.inputs"""
        process = CalculationFactory(self.ctx.calculation)
        running = self.submit(process, **self.ctx.inputs)
        return self.to_context(calculations=append_(running))

    def retrieve_results(self):
        """Process calculation results; adapted from aiida_vasp"""
        # return the results of the last calculation
        last_calc = self.ctx.calculations[-1]

        # check exit status of a last calc
        if last_calc.exit_status not in (None, 0):
            self.report(f'The calculations failed with exit message: {last_calc.exit_message}')
            exit_status = last_calc.exit_status // 100
            if exit_status == 3:
                return self.exit_codes.ERROR_CRYSTAL
            else:
                return self.exit_codes.UNKNOWN_ERROR

        for name, port in self.spec().outputs.items():
            if port.required and name not in last_calc.outputs:
                self.report('The spec specifies the output {} as required '
                            'but was not an output of {}<{}>'.format(name, self._calculation.__name__,
                                                                     last_calc.pk))

            if name in last_calc.outputs:
                self.out(name, last_calc.outputs[name])
        return

    def finalize(self):
        """Finalize calculation, clean remote directory if needed (adapted from aiida-vasp)"""
        if not self.inputs.clean_workdir:
            return
        cleaned_calcs = []
        for calculation in self.ctx.calculations:
            try:
                # noinspection PyProtectedMember
                calculation.outputs.remote_folder._clean()
                cleaned_calcs.append(calculation)
            except ValueError as ex:
                self.logger.warning("Exception caught while cleaning remote folders: {}".format(ex))
        if cleaned_calcs:
            self.report('Cleaned remote folders of calculations: {}'.format(' '.join(map(str, cleaned_calcs))))


class BasePropertiesWorkChain(WorkChain):
    """Run Properties calculation"""

    _calculation = 'crystal_dft.properties'

    @classmethod
    def define(cls, spec):
        super(BasePropertiesWorkChain, cls).define(spec)

        # define inputs
        spec.input('code', valid_type=Code)
        spec.input('wavefunction', valid_type=get_data_class('singlefile'), required=True)
        spec.input('parameters', valid_type=get_data_class('dict'), required=True)
        spec.input('options', valid_type=get_data_class('dict'), required=True, help="Calculation options")

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
            options_dict = self.inputs.options.get_dict()
            label = options_dict.pop('label', DEFAULT_TITLE)
            description = options_dict.pop('description', '')
            self.ctx.inputs.metadata = AttributeDict({'options': options_dict,
                                                      'label': label,
                                                      'description': description})

    def _set_default_parameters(self, parameters):
        """Set defaults to calculation parameters"""
        parameters_dict = parameters.get_dict()
        from aiida_crystal_dft.io.f9 import Fort9
        with self.inputs.wavefunction.open() as f:
            file_name = f.name
        wf = Fort9(file_name)
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
        return get_data_class('dict')(dict=parameters_dict)

    def run_calculation(self):
        """Run a calculation from self.ctx.inputs"""
        process = CalculationFactory(self._calculation)
        running = self.submit(process, **self.ctx.inputs)
        return self.to_context(calculations=append_(running))

    def retrieve_results(self):
        """Process calculation results; adapted from aiida_vasp"""
        # return the results of the last calculation
        last_calc = self.ctx.calculations[-1]
        for name, port in self.spec().outputs.items():
            if port.required and name not in last_calc.outputs:
                self.report('the spec specifies the output {} as required '
                            'but was not an output of {}<{}>'.format(name, self._calculation.__name__,
                                                                     last_calc.pk))

            if name in last_calc.outputs:
                # node = last_calc.outputs[name]
                self.out(name, last_calc.outputs[name])
                # self.report("attaching the node {}<{}> as '{}'".format(node.__class__.__name__, node.pk, name))
        return
