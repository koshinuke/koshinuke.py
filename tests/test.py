# -*- coding: utf-8 -*-
"""
    tests.test
    ~~~~~~~~~~

    Test suite runner.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import unittest

import auth_test
import core_test
import koshinuke_test


if __name__ == '__main__':
    alltests = unittest.TestSuite([auth_test.suite(),
                                   core_test.suite(),
                                   koshinuke_test.suite()])
    unittest.TextTestRunner(verbosity=2).run(alltests)
