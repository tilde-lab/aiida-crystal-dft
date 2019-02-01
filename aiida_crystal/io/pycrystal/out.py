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
    if not CRYSTOUT.acceptable(out_file):
        raise FileNotFoundError("{} is not a valid CRYSTAL output file".format(out_file))
    result = CRYSTOUT(out_file)

    return result.info
