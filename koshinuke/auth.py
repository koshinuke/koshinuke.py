# -*- coding: utf-8 -*-
"""
    koshinuke.auth
    ~~~~~~~~~~~~~~

    Implements the authentication.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

from crypt import crypt
import hashlib
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
    hashed_pass = hashlib.sha1()
    hashed_pass.update(password + encrypted_password[:40])
    return encrypted_password[40:] == hashed_pass.hexdigest()


def add_user(username, password, auth_key):
    """Add linux user, and register auth key to authorized_keys.
    sudo is required, and it should be not used by web app.
    """
    home_dir = os.path.join('/home', '{0}'.format(username))  # fixme
    call(['useradd',
          '--password', _generate_encrypted_password(username, password),
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


def _generate_encrypted_password(username, password):
    # todo: check security. is secure really? to more secure.
    # ref. http://pyramid.chromaticleaves.com/simpleauth/
    if isinstance(password, unicode):
        password_8bit = password.encode('utf-8')
    else:
        password_8bit = password

    salt = hashlib.sha1()
    salt.update(os.urandom(60))
    hash = hashlib.sha1()
    hash.update(password_8bit + salt.hexdigest())
    hashed_password = salt.hexdigest() + hash.hexdigest()

    if not isinstance(hashed_password, unicode):
        hashed_password = hashed_password.decode('utf-8')

    return hashed_password


def _get_salt(username):
    return ''.join([username, Config.FIXED_SALT])


class PermissionError(Exception):
    pass
