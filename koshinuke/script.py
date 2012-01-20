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


def usage():
    print("usage: script.py <add-user | create-project | create-repo>")


if __name__ == '__main__':
    args = sys.argv

    if len(args) != 2:
        usage()
        sys.exit(0)

    command = args[1]

    if command == 'add-user':
        username = raw_input('User Name:')
        password = getpass.getpass()
        auth_key = raw_input('Auth Key:')
        auth.add_user(username, password, auth_key)
        print("{0} is added.".format(username))
    elif command == 'create-project':
        project = raw_input('Project:')
        username = raw_input('User Name:')
        core.create_project(project, username)
        print("{0} is created.".format(project))
    elif command == 'create-repo':
        project = raw_input('Project:')
        repository = raw_input('Repository:')
        username = raw_input('User Name:')
        core.create_repository(project, repository, username)
        print("{0} is created.".format(repository))
    else:
        usage()
