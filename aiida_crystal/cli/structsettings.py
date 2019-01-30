"""An AiiDA node representing crystal structure along with symmetry operations"""
import click
from jsonextended import edict
from aiida import load_dbenv, is_dbenv_loaded
from aiida_crystal.aiida_compatibility import cmp_load_verdi_data

VERDI_DATA = cmp_load_verdi_data()

# TODO add tests


@VERDI_DATA.group('cry17-settings')
def structsettings():
    """Commandline interface for working with StructSettingsData"""


@structsettings.command()
@click.option(
    '--symmetries', '-s', is_flag=True, help="show full symmetry operations")
@click.argument('pk', type=int)
def show(pk, symmetries):
    """show the contents of a StructSettingsData"""
    if not is_dbenv_loaded():
        load_dbenv()
    from aiida.orm import load_node
    from aiida.orm import DataFactory

    node = load_node(pk)

    if not isinstance(node, DataFactory('crystal.structsettings')):
        click.echo(
            "The node was not of type 'crystal.structsettings'", err=True)
    elif symmetries:
        edict.pprint(node.data, print_func=click.echo, round_floats=5)
    else:
        edict.pprint(dict(node.iterattrs()), print_func=click.echo)


@structsettings.command()
def schema():
    """view the validation schema"""
    if not is_dbenv_loaded():
        load_dbenv()
    from aiida.orm import DataFactory
    data_schema = DataFactory('crystal.structsettings').data_schema
    edict.pprint(data_schema, depth=None, print_func=click.echo)
