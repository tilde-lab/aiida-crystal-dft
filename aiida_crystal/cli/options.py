"""Common click options for verdi commands"""
import click
from aiida.cmdline.params import options


FAMILY_NAME = options.OverridableOption(
    '--name', required=True, help='Name of the BasisSet family')
PATH = options.OverridableOption(
    '--path',
    default='.',
    type=click.Path(exists=True),
    help='Path to the folder')

DRY_RUN = options.OverridableOption(
    '--dry-run',
    is_flag=True,
    is_eager=True,
    help='do not commit to database or modify configuration files')

FORCE = options.FORCE
DESCRIPTION = options.DESCRIPTION
