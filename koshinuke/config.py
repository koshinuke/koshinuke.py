# -*- coding: utf-8 -*-
"""
    koshinuke.config
    ~~~~~~~~~~~~~~~~

    Implements the configuration.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""


class BaseConfig(object):
    EXCLUDED_PROJECTS = ['bin', 'lib', 'lib64', 'usr']

    CREATE_MESSAGE = "create repository."
    DEFAULT_COMMIT_MESSAGE = "updated by koshinuke."
    DEFAULT_README = "hello world!"


class ProductionConfig(BaseConfig):
    HOST = '<hostname>'
    PORT = 80
    DEBUG = False

    PROJECT_ROOT = '<koshinuke_project_root>'
    SYSTEM_AUTHOR = '<system_author>'
    SYSTEM_MAILADDRESS = '<system_mailaddress>'

    LOGFILE = '<log_file>'
    LOGLEVEL = 'WARNING'


class DevelopmentConfig(BaseConfig):
    HOST = 'localhost'
    PORT = 8080
    DEBUG = True

    PROJECT_ROOT = '/var/koshinuke/'
    SYSTEM_AUTHOR = 'koshinuke'
    SYSTEM_MAILADDRESS = 'koshinuke@example.com'

    LOGFILE = 'koshinuke.log'
    LOGLEVEL = 'DEBUG'


# mode
Config = DevelopmentConfig
