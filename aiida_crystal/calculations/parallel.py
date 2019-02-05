"""
Calculations provided by aiida_crystal.

Register calculations via the "aiida.calculations" entry point in setup.json.
"""

from aiida_crystal.calculations import CrystalCommonCalculation


class CrystalParallelCalculation(CrystalCommonCalculation):
    pass
