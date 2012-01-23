# -*- coding: utf-8 -*-
"""
    tests.core_test
    ~~~~~~~~~~~~~~~

    Tests core functions.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import os
import sys
import unittest

import utils

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from koshinuke import core
from koshinuke.config import Config


class CreateTestCase(unittest.TestCase):

    def setUp(self):
        utils.add_test_user()

    def tearDown(self):
        try:
            utils.destroy_test_repository()
            utils.destroy_test_project()
        except OSError:  # not exists
            pass
        utils.remove_test_user()

    def test_create_project(self):
        core.create_project(utils.EXPECTED_PROJECT, utils.EXPECTED_USERNAME)
        assert utils.exists_test_project()

    def test_create_repository(self):
        core.create_repository(utils.EXPECTED_PROJECT,
                               utils.EXPECTED_REPOSITORY,
                               utils.EXPECTED_USERNAME)
        assert utils.exists_test_repository()


class UpdateTestCase(unittest.TestCase):

    def setUp(self):
        utils.create_test_project()
        utils.create_test_repository()

    def tearDown(self):
        utils.destroy_test_repository()
        utils.destroy_test_project()

    def test_update_resource(self):
        objectid = utils.get_test_current_objectid()
        content = 'updated by test.'
        core.update_resource(utils.EXPECTED_PROJECT, utils.EXPECTED_REPOSITORY,
                             utils.EXPECTED_BRANCH, utils.EXPECTED_RESOURCE,
                             content, objectid=objectid)
        assert utils.get_test_blob_content() == content


class GetTestCase(unittest.TestCase):

    def setUp(self):
        utils.create_test_project()
        utils.create_test_repository()

    def tearDown(self):
        utils.destroy_test_repository()
        utils.destroy_test_project()

    def test_get_projects(self):
        projects = core.get_projects()
        assert utils.EXPECTED_PROJECT in projects

    def test_get_repositories(self):
        repositories = core.get_repositories(utils.EXPECTED_PROJECT)
        assert utils.EXPECTED_REPOSITORY in repositories

    def test_get_history(self):
        history = core.get_history(utils.EXPECTED_PROJECT,
                                   utils.EXPECTED_REPOSITORY)
        for h in history:
            h['activities'] = []
        assert history == utils.load_json('history.json')
        # todo: add validation for activities

    def test_get_resource(self):
        resource = core.get_resource(utils.EXPECTED_PROJECT,
                                     utils.EXPECTED_REPOSITORY,
                                     utils.EXPECTED_BRANCH,
                                     utils.EXPECTED_RESOURCE)
        assert resource == utils.load_json('blob.json')

        resource = core.get_resource(utils.EXPECTED_PROJECT,
                                     utils.EXPECTED_REPOSITORY,
                                     utils.EXPECTED_REV,
                                     utils.EXPECTED_RESOURCE)
        assert resource == utils.load_json('blob_rev.json')
        # todo: add test for nested resource

    def test_get_resources(self):
        resources = core.get_resources(utils.EXPECTED_PROJECT,
                                       utils.EXPECTED_REPOSITORY,
                                       utils.EXPECTED_BRANCH)
        assert resources == utils.load_json('tree.json')

        resources = core.get_resources(utils.EXPECTED_PROJECT,
                                       utils.EXPECTED_REPOSITORY,
                                       utils.EXPECTED_REV)
        assert resources == utils.load_json('tree_rev.json')

        resources = core.get_resources(utils.EXPECTED_PROJECT,
                                       utils.EXPECTED_REPOSITORY,
                                       utils.EXPECTED_BRANCH,
                                       limit=utils.EXPECTED_LIMIT)
        assert resources == utils.load_json('tree_limit.json')
        # todo: add test for nested resource
        # todo: add test for offset
        # todo: add test for case that commit has no parent

    def test_get_commits(self):
        commits = core.get_commits(utils.EXPECTED_PROJECT,
                                   utils.EXPECTED_REPOSITORY,
                                   utils.EXPECTED_BRANCH)
        assert commits == utils.load_json('commits.json')

        commits = core.get_commits(utils.EXPECTED_PROJECT,
                                   utils.EXPECTED_REPOSITORY,
                                   utils.EXPECTED_REV)
        assert commits == utils.load_json('commits_rev.json')

        commits = core.get_commits(utils.EXPECTED_PROJECT,
                                   utils.EXPECTED_REPOSITORY,
                                   utils.EXPECTED_BRANCH,
                                   limit=utils.EXPECTED_LIMIT)
        assert commits == utils.load_json('commits_limit.json')

        commits = core.get_commits(utils.EXPECTED_PROJECT,
                                   utils.EXPECTED_REPOSITORY,
                                   utils.EXPECTED_BRANCH,
                                   path=utils.EXPECTED_RESOURCE)
        assert commits == utils.load_json('commits_path.json')
        # todo: add test for nested resource

    def test_get_commit(self):
        commit = core.get_commit(utils.EXPECTED_PROJECT,
                                 utils.EXPECTED_REPOSITORY,
                                 utils.EXPECTED_REV)
        assert commit == utils.load_json('commit.json')

    def test_get_branches(self):
        branches = core.get_branches(utils.EXPECTED_PROJECT,
                                     utils.EXPECTED_REPOSITORY)
        branches['host'] = utils.EXPECTED_HOST
        assert branches == utils.load_json('branches.json')

    def test_get_tags(self):
        tags = core.get_tags(utils.EXPECTED_PROJECT, utils.EXPECTED_REPOSITORY)
        tags['host'] = utils.EXPECTED_HOST
        assert tags == utils.load_json('tags.json')


def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(CreateTestCase))
    suite.addTest(loader.loadTestsFromTestCase(UpdateTestCase))
    suite.addTest(loader.loadTestsFromTestCase(GetTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
