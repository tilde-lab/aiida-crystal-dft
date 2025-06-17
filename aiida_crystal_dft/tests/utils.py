"""Helper functions for tests"""

from aiida.orm import User, AuthInfo
from aiida.common import NotExistent


def get_current_user():
    """Returns the current AiiDA user"""
    return User.collection.get_default()


def get_authinfo(computer):
    """Get existing authinfo or create one if not in place"""
    try:
        authinfo = computer.get_authinfo(get_current_user())
    except NotExistent:
        authinfo = AuthInfo(computer=computer, user=get_current_user())
        authinfo.store()
    return authinfo
