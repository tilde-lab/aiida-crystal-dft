#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
A workchain (almost?) copying the workflow of runcry executable
"""

from aiida.engine import WorkChain
from aiida.orm import Code
from aiida.common.extendeddicts import AttributeDict
from aiida_crystal.utils import get_data_class
from aiida_crystal.workflows.base import BaseCrystalWorkChain, BasePropertiesWorkChain


class RunCryWorkChain(WorkChain):
    """Run a kind of calculation associated with runcry script, namely, run CRYSTAL and properties in the same run.
    Try to make an intelligent guess of band and dos input in case it is asked for, but not provided.
    """

    @classmethod
    def define(cls, spec):
        super(RunCryWorkChain, cls).define(spec)
        # define inputs
        spec.input('crystal_code', valid_type=Code)
        spec.input('properties_code', valid_type=Code)
        spec.expose_inputs(BaseCrystalWorkChain, include=['structure', 'basis_family'])
        spec.input('crystal_parameters', valid_type=get_data_class('parameter'), required=True)
        spec.input('properties_parameters', valid_type=get_data_class('parameter'), required=True)
        spec.input('options', valid_type=get_data_class('parameter'), required=True, help="Calculation options")
        # define workchain routine
        spec.outline(cls.init_inputs,
                     cls.run_crystal_calc,
                     cls.run_properties_calc,
                     cls.retrieve_results)
        # define outputs
        spec.expose_outputs(BaseCrystalWorkChain)
        spec.expose_outputs(BasePropertiesWorkChain)

    def init_inputs(self):
        self.ctx.inputs = AttributeDict()
        self.ctx.inputs.crystal = AttributeDict()
        self.ctx.inputs.properties = AttributeDict()
        # set the crystal workchain inputs
        self.ctx.inputs.crystal.code = self.inputs.crystal_code
        self.ctx.inputs.crystal.structure = self.inputs.structure
        self.ctx.inputs.crystal.parameters = self.inputs.crystal_parameters
        self.ctx.inputs.crystal.basis_family = self.inputs.basis_family
        self.ctx.inputs.crystal.options = self.inputs.options
        # set the properties workchain inputs
        self.ctx.inputs.properties.code = self.inputs.properties_code
        self.ctx.inputs.properties.parameters = self.inputs.properties_parameters
        self.ctx.inputs.properties.options = self.inputs.options
        # properties wavefunction input must be set after crystal run

    def run_crystal_calc(self):
        crystal_run = self.submit(BaseCrystalWorkChain, **self.ctx.inputs.crystal)
        return self.to_context(crystal=crystal_run)

    def run_properties_calc(self):
        self.ctx.inputs.properties.wavefunction = self.ctx.crystal.out.output_wavefunction
        properties_run = self.submit(BasePropertiesWorkChain, **self.ctx.inputs.properties)
        return self.to_context(properties=properties_run)

    def retrieve_results(self):
        self.out_many(self.exposed_outputs(self.ctx.crystal, BaseCrystalWorkChain))
        self.out_many(self.exposed_outputs(self.ctx.properties, BasePropertiesWorkChain))
