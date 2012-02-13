# -*- coding: utf-8 -*-
"""
    koshinuke.script
    ~~~~~~~~~~~~~~~~

    Helper script that manage user, project and repository.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import sys
import getpass

import auth
import core


def add_user():
    username = raw_input('User Name:')
    password = getpass.getpass()
    auth_key = raw_input('Auth Key:')
    auth.add_user(username, password, auth_key)
    print("A user is added: {0}".format(username))


def add_project():
    project = raw_input('Project:')
    username = raw_input('User Name:')
    core.create_project(project, username)
    print("A project is added: {0}".format(project))


def add_repository():
    project = raw_input('Project:')
    repository = raw_input('Repository:')
    username = raw_input('User Name:')
    core.create_repository(project, repository, username)
    print("A repository is added: {0}/{1}".format(project, repository))
