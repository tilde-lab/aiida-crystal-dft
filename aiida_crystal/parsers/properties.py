#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.

from aiida.parsers.parser import Parser
# from aiida.parsers.exceptions import OutputParsingError
# from aiida.orm import CalculationFactory


class PropertiesParser(Parser):
    """
    Parser class for parsing output of CRYSTAL calculation.
    """

    # pylint: disable=protected-access
    def __init__(self, calculation):
        """
        Initialize Parser instance
        """
        super(PropertiesParser, self).__init__(calculation)
