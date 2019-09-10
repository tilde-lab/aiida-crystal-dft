""" tests for the plugin that does not pollute your profiles/databases.
"""
import os

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
INPUT_FILES_DIR = os.path.join(TEST_DIR, 'input_files')
OUTPUT_FILES_DIR = os.path.join(TEST_DIR, 'output_files')
MOCK_DIR = os.path.join(TEST_DIR, 'mock_codes')
