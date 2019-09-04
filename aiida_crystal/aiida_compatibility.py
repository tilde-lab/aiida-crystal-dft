"""Utilities for working with different versions of aiida"""

import json
import datetime
from functools import wraps
from packaging import version


def aiida_version():
    """get the version of aiida in use

    :returns: packaging.version.Version
    """
    from aiida import __version__ as aiida_version_
    return version.parse(aiida_version_)


def cmp_version(string):
    """convert a version string to a packaging.version.Version"""
    return version.parse(string)


def cmp_load_verdi_data():
    """Load the verdi data click command group for any version since 0.11."""
    verdi_data = None
    import_errors = []

    try:
        from aiida.cmdline.commands import data_cmd as verdi_data
    except ImportError as err:
        import_errors.append(err)

    if not verdi_data:
        try:
            from aiida.cmdline.commands import verdi_data
        except ImportError as err:
            import_errors.append(err)

    if not verdi_data:
        try:
            from aiida.cmdline.commands.cmd_data import verdi_data
        except ImportError as err:
            import_errors.append(err)

    if not verdi_data:
        err_messages = '\n'.join(
            [' * {}'.format(error) for error in import_errors])
        raise ImportError(
            'The verdi data base command group could not be found:\n' +
            err_messages)

    return verdi_data


def run_get_node(process, inputs_dict):
    """ an implementation of run_get_node which is compatible with both aiida v0.12 and v1.0.0

    it will also convert "options" "label" and "description" to/from the _ variant

    :param process: a process
    :param inputs_dict: a dictionary of inputs
    :type inputs_dict: dict
    :return: the calculation Node
    """
    from aiida.engine.launch import run_get_node  # pylint: disable=import-error
    for key in ["_options", "_label", "_description"]:
        if key in inputs_dict:
            inputs_dict[key[1:]] = inputs_dict.pop(key)
    _, calcnode = run_get_node(process, **inputs_dict)

    return calcnode


def get_data_node(data_type, *args, **kwargs):
    return get_data_class(data_type)(*args, **kwargs)


def get_data_class(data_type):
    """
    Provide access to the orm.data classes with deferred dbenv loading.

    compatibility: also provide access to the orm.data.base members, which are loadable through the
    DataFactory as of 1.0.0-alpha only.
    """
    from aiida.plugins import DataFactory
    data_cls = DataFactory(data_type)
    return data_cls


BASIC_DATA_TYPES = {'bool', 'float', 'int', 'list', 'str'}


def get_automatic_user():
    from aiida.orm import User
    return User.objects.get_default()


def json_default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    return None


def get_calc_log(calcnode):
    """get a formatted string of the calculation log"""
    from aiida.backends.utils import get_log_messages

    log_string = "- Calc State:\n{0}\n- Scheduler Out:\n{1}\n- Scheduler Err:\n{2}\n- Log:\n{3}" \
                 "".format(calcnode.get_state(),
                           calcnode.get_scheduler_output(),
                           calcnode.get_scheduler_error(),
                           json.dumps(get_log_messages(calcnode), default=json_default, indent=2))
    return log_string

