#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

import click
import tabulate
from click_spinner import spinner as cli_spinner
from aiida.cmdline.commands.cmd_data import verdi_data
from aiida_crystal.aiida_compatibility import get_data_class
from aiida_crystal.cli import options


@verdi_data.group('crystal')
def basis_set():
    """Commandline interface for working with Crystal Basis Set Data"""


@basis_set.command()
@options.PATH(help='Path to a folder containing the Basis Set files')
@click.option('--ext', default="basis", help="the file extension to filter by")
@options.FAMILY_NAME()
def uploadfamily(path, ext, name, description, stop_if_existing, dry_run):
    """Upload a family of CRYSTAL Basis Set files."""

    basis_data_cls = get_data_class('crystal.basisset')
    with cli_spinner():
        nfiles, num_uploaded = basis_data_cls.upload_basisset_family(
            path,
            name,
            description,
            stop_if_existing=stop_if_existing,
            extension=".{}".format(ext),
            dry_run=dry_run)

    click.echo(
        'Basis Set files found and added to family: {}, of those {} were newly uploaded'.
        format(nfiles, num_uploaded))
    if dry_run:
        click.echo('No files were uploaded due to --dry-run.')


@basis_set.command()
@click.option(
    '-e',
    '--element',
    multiple=True,
    help='Filter for families containing potentials for all given elements.')
@click.option('-p', '--list-pks', is_flag=True)
def listfamilies(element, with_description, list_pks):
    """List available families of CRYSTAL Basis Set files."""

    basis_data_cls = get_data_class('crystal.basisset')
    groups = basis_data_cls.get_basis_groups(filter_elements=element)

    table = [['Family', 'Num Basis Sets']]
    if with_description:
        table[0].append('Description')
    if list_pks:
        table[0].append('Pks')
    for group in groups:
        row = [group.name, len(group.nodes)]
        if with_description:
            row.append(group.description)
        if list_pks:
            row.append(",".join([str(n.pk) for n in group.nodes]))
        table.append(row)
    if len(table) > 1:
        click.echo(tabulate.tabulate(table, headers='firstrow'))
        click.echo()
    elif element:
        click.echo(
            'No Basis Set family contains all given elements and symbols.')
    else:
        click.echo('No Basis Set family available.')
