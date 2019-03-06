""" Base workflows for CRYSTAL code. These are meant to handle failures/restarts/etc...
"""

from aiida.orm import CalculationFactory
from aiida.orm.code import Code
from aiida.common.extendeddicts import AttributeDict
from aiida.work.workchain import WorkChain, append_
from aiida_crystal.aiida_compatibility import get_data_class
from aiida_crystal.data.basis_set import get_basissets_from_structure


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
        pass



