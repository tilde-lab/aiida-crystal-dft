"""
initialise a text database and profile
"""
import tempfile
import shutil

from aiida.manage.fixtures import fixture_manager
import pytest


pytest_plugins = [
   "aiida_crystal_dft.tests.fixtures.basis",
   "aiida_crystal_dft.tests.fixtures.calculations",
   "aiida_crystal_dft.tests.fixtures.code",
]


@pytest.fixture(scope='session')
def aiida_profile():
    """setup a test profile for the duration of the tests"""
    with fixture_manager() as fixture_mgr:
        yield fixture_mgr


@pytest.fixture(scope='function')
def new_database(aiida_profile):
    """clear the database after each test"""
    yield aiida_profile
    aiida_profile.reset_db()


@pytest.fixture(scope='session')
def new_workdir():
    """get a new temporary folder to use as the computer's wrkdir"""
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)
