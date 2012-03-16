# -*- coding: utf-8 -*-
"""
    koshinuke.config
    ~~~~~~~~~~~~~~~~

    Implements the configuration.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import socket
import urllib2


# helper functions
def find_host(is_public):
    if is_public:
        ip = urllib2.urlopen('http://ipcheck.ieserver.net').read()
        return socket.gethostbyaddr(ip)[0]
    else:
        return socket.gethostname()


# configurations
class BaseConfig(object):
    USER_GROUP = 'knusers'

    CREATE_MESSAGE = "create repository."
    DEFAULT_COMMIT_MESSAGE = "updated by koshinuke."
    DEFAULT_README = "hello world!"

    EXCLUDED_PROJECTS = ['bin', 'lib', 'lib64', 'usr']


class ProductionConfig(BaseConfig):
    HOST = '<hostname>'
    PORT = 80
    DEBUG = False

    SECRET_KEY = '<secret_key>'

    PROJECT_ROOT = '<koshinuke_project_root>'
    SYSTEM_AUTHOR = '<system_author>'
    SYSTEM_MAILADDRESS = '<system_mailaddress>'

    LOGFILE = '<log_file>'
    LOGLEVEL = 'WARNING'


class DevelopmentConfig(BaseConfig):
    HOST = 'localhost'
    PORT = 8080
    DEBUG = True

    SECRET_KEY = 'koshinuke_default_secret_key'

    PROJECT_ROOT = '/var/koshinuke/'
    SYSTEM_AUTHOR = 'koshinuke'
    SYSTEM_MAILADDRESS = 'koshinuke@example.com'

    LOGFILE = 'koshinuke.log'
    LOGLEVEL = 'DEBUG'


class AutoConfig(DevelopmentConfig):
    HOST = find_host(is_public=True)
    PORT = 80


# mode
Config = AutoConfig
