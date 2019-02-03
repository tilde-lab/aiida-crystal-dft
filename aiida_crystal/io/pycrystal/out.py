"""
Pycrystal-based CRYSTAL output parser
"""

from pycrystal import CRYSTOUT


def parse(out_file):
    """
     An adapter from pycrystal format to AiiDA output_parameters format, consistent with AiiDA-quantumespresso
    :param out_file: A name of file to parse
    :return: Parsed data
    """
    out_params = {}
    if not CRYSTOUT.acceptable(out_file):
        raise FileNotFoundError("{} is not a valid CRYSTAL output file".format(out_file))
    result = CRYSTOUT(out_file)
    info = result.info
    # Parameters from pycrystal parsing result as given in pwscf output-parameters
    out_params['creator_name'] = "CRYSTAL"
    out_params['creator_version'] = info['prog']
    out_params['exchange_correlation'] = info['H']   # dft prefix omitted as there can be HF calculations
    out_params['energy'] = info['energy']
    out_params['energy_units'] = 'eV'  # pycrystal converts Ha to eV
    out_params['energy_accuracy'] = abs(info['e_accuracy'])
    out_params['energy_accuracy_units'] = 'eV'  # this also is converted
    out_params['monkhorst_pack_grid'] = [int(i) for i in info['k'].split('x')]
    out_params['number_of_atoms'] = info['n_atoms']
    out_params['number_of_electrons'] = info['n_electrons']
    out_params['number_of_symmetries'] = info['n_symops']
    out_params['parser_info'] = 'pycrystal 1.0.0.2'
    out_params['parser_warnings'] = info['warns']
    out_params['scf_iterations'] = info['ncycles']   # a list of scf iteration numbers at each ionic step
    return out_params
