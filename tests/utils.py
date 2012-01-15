# -*- coding: utf-8 -*-
"""
    tests.utils
    ~~~~~~~~~~~

    Utilities.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import json
import os
from pwd import getpwnam
from shutil import rmtree
from subprocess import call
import sys

from git import Repo

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, 'data')

sys.path.append(os.path.join(here, '..'))

from koshinuke.config import Config

EXPECTED_PROJECT = 'testproject'
EXPECTED_REPOSITORY = 'testrepo'
EXPECTED_BRANCH = 'master'
EXPECTED_RESOURCE = 'README'
EXPECTED_REV = '98d540096e7d21f2e53b4e799fb851715ed17e85'
EXPECTED_LIMIT = 1
EXPECTED_HOST = 'example.com'

EXPECTED_USERNAME = 'testuser'
EXPECTED_PASSWORD = 'testpassword'
EXPECTED_AUTH_KEY = 'ssh-rsa //KOSHINUKE+DUMMY+SSH+KEY// koshinuke@example.com'


def create_test_project(project=None):
    os.mkdir(_test_project_path(project))


def destroy_test_project(project=None):
    rmtree(_test_project_path(project))


def create_test_repository(repository=None):
    _org_repository().clone(_test_repository_path(repository), bare=True)


def destroy_test_repository(repository=None):
    rmtree(_test_repository_path(repository))


def get_test_repository(repository=None):
    return Repo(_test_repository_path(repository))


def get_test_current_rev():
    return get_test_repository().commit().hexsha


def get_test_blob_content():
    repo = get_test_repository()
    return repo.commit().tree[EXPECTED_RESOURCE].data_stream.read()


def exists_test_project():
    return os.path.exists(_test_project_path())


def exists_test_repository():
    return os.path.exists(_test_repository_path())


def add_test_user():
    home_dir = os.path.join('/home', '{0}'.format(EXPECTED_USERNAME))
    call(['useradd',
          '--password', EXPECTED_PASSWORD,
          '--home-dir', home_dir, '--create-home',
          '--groups', Config.USER_GROUP,
          '--shell', '/bin/bash',
          EXPECTED_USERNAME])
    uid, gid = getpwnam(EXPECTED_USERNAME)[2:4]


def remove_test_user():
    call(['userdel', '--remove', EXPECTED_USERNAME])


def load_json(filename):
    return json.load(open(os.path.join(data_dir, filename), 'r'))


def _test_project_path(project=None):
    if not project:
        project = EXPECTED_PROJECT
    return os.path.join(Config.PROJECT_ROOT, project)


def _test_repository_path(repository=None):
    if not repository:
        repository = EXPECTED_REPOSITORY
    return os.path.join(_test_project_path(), '{0}.git'.format(repository))


def _org_repository():
    return Repo(os.path.join(data_dir, '{0}.git'.format(EXPECTED_REPOSITORY)))
