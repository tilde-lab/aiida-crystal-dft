#!/usr/bin/env python
"""
A setup script
"""

import json
from setuptools import setup, find_packages
# from importlib import import_module

if __name__ == '__main__':
    # Provide static information in setup.json
    # such that it can be discovered automatically
    with open('setup.json', 'r') as info:
        kwargs = json.load(info)
    setup(
        packages=find_packages(),
        # version=import_module('aiida_crystal').__version__,
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        **kwargs)
