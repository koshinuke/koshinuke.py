# -*- coding: utf-8 -*-
"""
    tests.auth_test
    ~~~~~~~~~~~~~~~

    Tests auth functions.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import os
import pwd
import sys
import unittest

import utils

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from koshinuke import auth
from koshinuke.config import Config


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if self._user_exists(utils.EXPECTED_USERNAME):
            auth.remove_user(utils.EXPECTED_USERNAME)
        # todo: do not use 'auth.remove_user' for test

    def test_authenticate(self):
        auth.add_user(utils.EXPECTED_USERNAME, utils.EXPECTED_PASSWORD,
                      utils.EXPECTED_AUTH_KEY)
        if auth.authenticate(utils.EXPECTED_USERNAME, utils.EXPECTED_PASSWORD):
            assert True
        else:
            assert False
        if auth.authenticate('invalid_user_name', utils.EXPECTED_PASSWORD):
            assert False
        else:
            assert True
        if auth.authenticate(utils.EXPECTED_USERNAME, 'invalid_password'):
            assert False
        else:
            assert True
        # todo: do not use 'auth.add_user' for test

    def test_add_user(self):
        auth.add_user(utils.EXPECTED_USERNAME, utils.EXPECTED_PASSWORD,
                      utils.EXPECTED_AUTH_KEY)
        assert self._user_exists(utils.EXPECTED_USERNAME)

    def test_remove_user(self):
        auth.add_user(utils.EXPECTED_USERNAME, utils.EXPECTED_PASSWORD,
                      utils.EXPECTED_AUTH_KEY)
        auth.remove_user(utils.EXPECTED_USERNAME)
        assert not self._user_exists(utils.EXPECTED_USERNAME)
        # todo: do not use 'auth.add_user' for test

    def _user_exists(self, username):
        try:
            pwd.getpwnam(username)[0]  # user exists
        except KeyError:
            return False
        home_dir = os.path.join('/home', '{0}'.format(username))
        auth_key_file = os.path.join(home_dir, '.ssh', 'authorized_keys')
        if not os.path.exists(home_dir):  # user home not exists
            return False
        if not os.path.exists(auth_key_file):  # authorized_keys not exists
            return False
        return True


def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(AuthTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
