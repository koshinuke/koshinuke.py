# -*- coding: utf-8 -*-
"""
    koshinuke.auth
    ~~~~~~~~~~~~~~

    Implements the authentication.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

from crypt import crypt
import os
from pwd import getpwnam
from spwd import getspnam
from subprocess import call

from config import Config


def authenticate(username, password):
    try:
        encrypted_password = getspnam(username)[1]
    except KeyError:
        # User is not existed, or koshinuke app is not permitted
        # to access shadow password database.
        return False
    return _get_encrypted_password(username, password) == encrypted_password


def add_user(username, password, auth_key):
    """Add linux user, and register auth key to authorized_keys.
    sudo is required, and it should be not used by web app.
    """
    home_dir = os.path.join('/home', '{0}'.format(username))  # fixme
    call(['useradd',
          '--password', _get_encrypted_password(username, password),
          '--home-dir', home_dir, '--create-home',
          '--groups', Config.USER_GROUP,
          '--shell', '/bin/bash',
          username])
    try:
        uid, gid = getpwnam(username)[2:4]
    except KeyError:
        raise PermissionError("User is can not be created. "\
                              "Maybe, permission denied.")
    ssh_dir = os.path.join(home_dir, '.ssh')
    os.mkdir(ssh_dir)
    auth_key_file = os.path.join(ssh_dir, 'authorized_keys')
    with open(auth_key_file, 'w') as f:
        f.write(auth_key)
    os.chown(auth_key_file, uid, gid)
    os.chmod(auth_key_file, 0600)
    os.chown(ssh_dir, uid, gid)
    os.chmod(ssh_dir, 0700)


def remove_user(username):
    call(['userdel', '--remove', username])


def _get_encrypted_password(username, password):
    return crypt(password, _get_salt(username))


def _get_salt(username):
    return ''.join([username, Config.FIXED_SALT])


class PermissionError(Exception):
    pass
