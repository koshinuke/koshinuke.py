# -*- coding: utf-8 -*-
"""
    tests.test
    ~~~~~~~~~~

    Test suite runner.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import unittest

import core_test
import koshinuke_test


if __name__ == '__main__':
    alltests = unittest.TestSuite([core_test.suite(), koshinuke_test.suite()])
    unittest.TextTestRunner(verbosity=2).run(alltests)
