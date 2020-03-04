"""A reader and writer for CRYSTAL d12 input file
"""
import os
from aiida_crystal.validation import read_schema, validate_with_json
from jinja2 import Template


class D12Formatter(object):
    """A class that formats the values according to JSON schema"""
    def __init__(self, schema=None):
        if schema is None:
            schema = read_schema("d12")
        self._schema = schema

    def format(self, key, value, keyword=None, ending=None):
        """
        Formats a value from the dict based on its type from schema
        :param key: a list of keys for the schema
        :param value: parameter value
        :param keyword: optional keyword as the title
        :param ending: optional ending for the parameter
        :return: a list of strings
        """
        type_formatter = {
            "string": self._format_string,
        }
        value_type = self._schema

    @staticmethod
    def _format_string(key, value, keyword, ending):
        return [value]

    def get_value_type(self, key, schema=None):
        if schema is None:
            schema = self._schema
        if len(key) == 1:
            if "type" in schema["properties"][key[0]]:
                return schema["properties"][key[0]]["type"]
            # oneOf?
        return self.get_value_type(key[1:], schema["properties"][key[0]])


class D12(object):
    """A reader and writer of INPUT (or input.d12) CRYSTAL file"""

    def __init__(self, parameters=None, basis=None):
        self._input = None
        if parameters is not None:
            self.use_parameters(parameters)
        self._basis = None
        if basis is not None:
            self.use_basis(basis)
        # geometry is EXTERNAL

    def read(self, f):
        raise NotImplementedError

    def __str__(self):
        if self._input is None:
            raise ValueError("Can not make input file out of empty dict")
        dirpath = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dirpath, "d12.schema")) as schema_file:
            template = Template(schema_file.read())
        return template.render(**self._input)

    def _geometry_block(self):
        geom_dict = self._input.get("geometry", {})
        lines = ["EXTERNAL"]
        # information
        lines += geom_dict.get("info_print", [])
        lines += geom_dict.get("info_external", [])
        # optimization
        opt_dict = geom_dict.get("optimise", False)
        if opt_dict:
            if isinstance(opt_dict, bool):
                opt_dict = {}
            lines.append("OPTGEOM")
            lines += opt_dict.get("info_print", [])
            lines += [opt_dict[key] for key in ["type", "hessian", "gradient"] if key in opt_dict]
            if "convergence" in opt_dict:
                lines += ["{}\n{}".format(k, v) for k, v in opt_dict["convergence"].items()]
            lines.append("ENDOPT")
        # phonons
        freq_dict = geom_dict.get("phonons", False)
        if freq_dict:
            if isinstance(freq_dict, bool):
                freq_dict = {}
            lines.append("FREQCALC")

            lines += freq_dict.get("info_print", [])
            # lines += [freq_dict[key] for key in ["type", "hessian", "gradient"] if key in freq_dict]
            # if "ir" in freq_dict:
            #     lines += ["{}\n{}".format(k, v) for k, v in freq_dict["convergence"].items()]
            # lines.append("ENDOPT")

        lines.append("END")
        return

    def write(self):
        """Writing input to file"""
        if self._input is None:
            raise ValueError("No ParameterData is associated with the input")
        if self._basis is None:
            raise ValueError("No BasisSet is associated with the input")

    def use_parameters(self, parameters):
        """A ParameterData (or a simple dict) to use for making INPUT"""
        input_dict = parameters if isinstance(parameters, dict) else parameters.get_dict()
        validate_with_json(input_dict, name="d12")
        self._input = input_dict

    def use_basis(self, basis):
        """A BasisSetData to use for making INPUT"""
        self._basis = basis
