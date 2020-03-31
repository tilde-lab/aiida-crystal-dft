#   Copyright (c)  Andrey Sobolev, 2020. Distributed under MIT license, see LICENSE file.

import os
from jinja2 import Environment, FileSystemLoader


def get_template(schema='d12.j2'):
    template_dir = os.path.dirname(__file__)
    env = Environment(loader=FileSystemLoader(template_dir),
                      lstrip_blocks=True,
                      trim_blocks=True,
                      keep_trailing_newline=True)
    return env.get_template(schema)
