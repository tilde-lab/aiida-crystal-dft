"""Utility functions for input/output files
"""


from pyparsing import ParseException


def _parse_string(parser, string):
    try:
        parsed_data = parser.parseString(string)
    except ParseException as p_e:
        # complete the error message
        msg = "ERROR during parsing of line %d:" % p_e.lineno
        msg += '\n' + '-' * 40 + '\n'
        msg += p_e.line + '\n'
        msg += ' ' * (p_e.col - 1) + '^\n'
        msg += '-' * 40 + '\n' + p_e.msg
        p_e.msg = msg
        raise
    return parsed_data
