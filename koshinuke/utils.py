# -*- coding: utf-8 -*-
"""
    koshinuke.utils
    ~~~~~~~~~~~~~~~

    Implements various utilities.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import hashlib
import json
import random

from config import Config

if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange

_MAX_CSRF_KEY = 18446744073709551616L  # 2 << 63


def jsonify(data):
    return json.dumps(data, ensure_ascii=False)


def generate_csrf_token():
    # see Flask-SeaSurf http://packages.python.org/Flask-SeaSurf/
    salt = (randrange(0, _MAX_CSRF_KEY), Config.SECRET_KEY)
    return str(hashlib.sha1('{0}{1}'.format(*salt)).hexdigest())
