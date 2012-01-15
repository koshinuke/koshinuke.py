# -*- coding: utf-8 -*-
"""
    tests.koshinuke_test
    ~~~~~~~~~~~~~~~~~~~~

    Tests the routing layer.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

from HTMLParser import HTMLParser
import json
import os
import sys
import unittest

import utils

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from koshinuke import koshinuke
from koshinuke.config import Config


def get_path(path):
    paths = ['', 'dynamic', utils.EXPECTED_PROJECT, utils.EXPECTED_REPOSITORY]
    paths.extend(path)
    return '/'.join(paths)


class CsrfTokenExtractor(HTMLParser):

    def __init__(self, key, value):
        HTMLParser.__init__(self)
        self.key = key
        self.value = value
        self.csrf_token = ''

    def handle_starttag(self, tag, _attrs):
        attrs = dict(_attrs)
        if tag == 'input' and \
           self.key in attrs and attrs.get(self.key) == self.value:
            self.csrf_token = attrs.get('value')


def get_csrf_token(data, attr, value):
    extractor = CsrfTokenExtractor(attr, value)
    extractor.feed(data)
    extractor.close()
    return extractor.csrf_token


def login(app):
    csrf_token = get_csrf_token(app.get('/').data, 'name', 't')
    data = {'u': utils.EXPECTED_USERNAME, 'p': utils.EXPECTED_PASSWORD,
            't': csrf_token}
    return app.post('/login', data=data, follow_redirects=True)


class BeforeLoginTestCase(unittest.TestCase):

    def setUp(self):
        utils.add_test_user()

        koshinuke.app.config['TESTING'] = True
        self.app = koshinuke.app.test_client()

    def tearDown(self):
        utils.remove_test_user()

    def test_index(self):
        rv = self.app.get('/')
        assert 'Login' in  rv.data

    def test_login(self):
        rv = login(self.app)
        assert 'Home' in  rv.data

    def test_init(self):
        # todo: implement
        pass


class AfterLoginTestCase(unittest.TestCase):

    def setUp(self):
        utils.add_test_user()
        utils.create_test_project()
        utils.create_test_repository()

        koshinuke.app.config['TESTING'] = True
        self.app = koshinuke.app.test_client()
        login(self.app)

    def tearDown(self):
        utils.destroy_test_repository()
        utils.destroy_test_project()
        utils.remove_test_user()

    def test_branches(self):
        rv = self.app.get(get_path(['branches']))
        branches = json.loads(rv.data)
        branches['host'] = utils.EXPECTED_HOST
        assert branches == utils.load_json('branches.json')

    def test_tags(self):
        rv = self.app.get(get_path(['tags']))
        tags = json.loads(rv.data)
        tags['host'] = utils.EXPECTED_HOST
        assert tags == utils.load_json('tags.json')

    def test_tree_root(self):
        path = get_path(['tree', utils.EXPECTED_BRANCH])
        rv = self.app.get(path)
        assert json.loads(rv.data) == utils.load_json('tree.json')

        rv = self.app.get('{0}?limit={1}'.format(path, utils.EXPECTED_LIMIT))
        assert json.loads(rv.data) == utils.load_json('tree_limit.json')

    def test_tree(self):
        # todo: implement. test data is required to be updated.
        pass

    def test_blob(self):
        rv = self.app.get(get_path(['blob',
                                    utils.EXPECTED_BRANCH,
                                    utils.EXPECTED_RESOURCE]))
        assert json.loads(rv.data) == utils.load_json('blob.json')

        rv = self.app.get(get_path(['blob',
                                    utils.EXPECTED_REV,
                                    utils.EXPECTED_RESOURCE]))
        assert json.loads(rv.data) == utils.load_json('blob_rev.json')

    def test_history(self):
        rv = self.app.get(get_path(['history']))
        history = json.loads(rv.data)
        for h in history:
            h['activities'] = []
        assert history == utils.load_json('history.json')
        # todo: add validation for activities

    def test_commits_root(self):
        path = get_path(['commits', utils.EXPECTED_BRANCH])
        rv = self.app.get(path)
        assert json.loads(rv.data) == utils.load_json('commits.json')

        rv = self.app.get('{0}?limit={1}'.format(path, utils.EXPECTED_LIMIT))
        assert json.loads(rv.data) == utils.load_json('commits_limit.json')

        rv = self.app.get(get_path(['commits', utils.EXPECTED_REV]))
        assert json.loads(rv.data) == utils.load_json('commits_rev.json')

    def test_commits(self):
        rv = self.app.get(get_path(['commits',
                                    utils.EXPECTED_BRANCH,
                                    utils.EXPECTED_RESOURCE]))
        assert json.loads(rv.data) == utils.load_json('commits_path.json')

    def test_commit(self):
        rv = self.app.get(get_path(['commit', utils.EXPECTED_REV]))
        assert json.loads(rv.data) == utils.load_json('commit.json')

    def test_update_resource(self):
        rv = self.app.get(get_path(['blob',
                                    utils.EXPECTED_BRANCH,
                                    utils.EXPECTED_RESOURCE]))
        content = 'updated by test.'
        data = {'commit': utils.get_test_current_rev(), 'content': content}
        rv = self.app.post(get_path(['blob',
                                     utils.EXPECTED_BRANCH,
                                     utils.EXPECTED_RESOURCE]), data=data)
        assert 'success' in rv.data
        assert utils.get_test_blob_content() == content


def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(BeforeLoginTestCase))
    suite.addTest(loader.loadTestsFromTestCase(AfterLoginTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
