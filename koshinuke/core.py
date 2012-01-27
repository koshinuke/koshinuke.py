# -*- coding: utf-8 -*-
"""
    koshinuke.core
    ~~~~~~~~~~~~~~

    Implements core functions, and accesses git object.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

from base64 import b64encode
from datetime import datetime, timedelta
from grp import getgrnam
from itertools import chain
import os
from pwd import getpwnam
from shutil import rmtree
from tempfile import mkdtemp
from time import mktime

from git import Repo, NoSuchPathError, BadObject, GitCommandError

from config import Config


_EXCLUDED_PROJECTS = set(Config.EXCLUDED_PROJECTS)
_IMAGE_EXTS = set(['bmp', 'gif', 'png', 'jpg', 'jpeg', 'ico'])


def get_projects():
    projects = set([project for project in os.listdir(Config.PROJECT_ROOT)])
    return list(projects.difference(_EXCLUDED_PROJECTS))


def get_repositories(project):
    return [repo_dot_git[:-4]  # remove '.git'
            for repo_dot_git in os.listdir(_get_project_path(project))]


def get_history(project, repository, days=30):
    now = datetime.today()
    return [{'name': h.name,
             'path': h.name,
             'timestamp': h.commit.committed_date,
             'author': h.commit.author.name,
             'message': h.commit.message,
             'activities': [[int(mktime(
                                 (now - timedelta(days=i)).timetuple())),
                             h.commit.count(since='{0} days ago'.format(i + 1),
                                            until='{0} days ago'.format(i))]
                            for i in xrange(days)]}
            for h in _get_repo(project, repository).branches]


def get_resource(project, repository, rev, path):
    commit = _get_commit(project, repository, rev)
    try:
        blob = commit.tree[path]
    except KeyError:
        raise NotFoundError("path is not found: {0}".format(path))
    _, ext = os.path.splitext(path)
    if ext in _IMAGE_EXTS:  # content is image
        encoded_data = b64encode(blob.data_stream.read())
        content = 'data:image/{0};base64,{1}'.format(ext, encoded_data)
    else:  # content is text
        try:
            content = blob.data_stream.read().decode('utf-8')
        except UnicodeDecodeError:
            raise NotFoundError("maybe, path specified tree: {0}".format(path))
    return {'objectid': blob.hexsha,
            'author': commit.author.name,
            'message': commit.message,
            'timestamp': commit.committed_date,
            'contents': content}


def get_resources(project, repository, rev, path='', offset=0, limit=100):
    commit = _get_commit(project, repository, rev)

    # get limited trees and blobs
    if path and not path.endswith('/'):
        path = ''.join([path, '/'])
    if path:
        def subtree(r):
            if r.path.startswith(path):
                return True
            else:
                return False
    else:
        def subtree(r):
            return True
    trees = {}
    blobs = {}
    for r in filter(subtree, commit.tree.traverse())[offset:offset + limit]:
        if r.type == 'tree':
            trees[r.path] = r
        else:
            blobs[r.path] = r

    # setup dictionary object
    result = [{'name': t.name,
               'path': '/'.join([rev, t.path]),
               'children': len(t.blobs) + len(t.trees),
               'type': 'tree'} for t in trees.values()]
    if not commit.parents:
        result.extend([_blobdata(b, commit, rev) for b in blobs.values()])
    else:
        for c in chain([commit], commit.iter_parents()):
            if not blobs:
                break
            for changed_path in c.stats.files.keys():
                b = blobs.pop(changed_path, None)
                if b:  # there is changed_path in resouces
                    result.append(_blobdata(b, c, rev))
    return result


def get_commits(project, repository, ref, rev=None, path='', limit=30):
    commits = []
    if rev:
        child = _get_commit(project, repository, rev)
    else:
        child = _get_commit(project, repository, ref)
        commits.append(_commitdata(child))
        limit -= 1
    commits.extend([_commitdata(p) for p in child.iter_parents(
        paths=path, max_count=limit, first_parent=True)])
    return commits


def get_commit(project, repository, rev):
    commit = _get_commit(project, repository, rev)
    parents = commit.parents
    diffs = []
    for parent in parents:
        # todo: since git 1.7.8, I can use --function-context option.
        for d in commit.diff(parent, create_patch=True):
            """Git-Python 0.3.2 RC1 has a bug, so diff.new_file is operation
            'delete' and diff.deleted_file is operation 'add'."""
            if d.new_file:
                operation = 'delete'
            elif d.deleted_file:
                operation = 'add'
            elif d.renamed:
                operation = 'rename'
            else:
                operation = 'modify'
            diff = {'a_path': d.a_blob.path,
                    'b_path': d.b_blob.path,
                    'operation': operation,
                    'patch': d.diff.decode('utf-8')}
            if operation == 'rename' or operation == 'modify':
                diff.update({'content':
                    d.b_blob.data_stream.read().decode('utf-8')})
            diffs.append(diff)
    return {'commit': rev, 'parent': [p.hexsha for p in parents],
            'diff': diffs, 'stats': {'files': commit.stats.files,
                                     'total': commit.stats.total},
            'timestamp': commit.committed_date,
            'author': commit.author.name,
            'message': commit.message}


def get_branches(project, repository, offset=0, limit=100):
    return _get_ref(project, repository, 'branches', offset, limit)


def get_tags(project, repository, offset=0, limit=100):
    return _get_ref(project, repository, 'tags', offset, limit)


def update_resource(project, repository, rev, path, content, message=None,
                    objectid=None):
    if not objectid:
        repo_is_empty = False
        try:
            _get_repo(project, repository).commit()
        except ValueError:  # repository is empty
            repo_is_empty = True
        if not repo_is_empty:
            raise CanNotUpdateError("Repository is not empty. "
                                    "Specify objectid.")
    else:
        if not rev in set([h.name for h
                           in _get_repo(project, repository).branches]):
            raise CanNotUpdateError("Specify a branch name for rev.")
        try:
            blob = _get_commit(project, repository, rev).tree[path]
        except KeyError:
            raise CanNotUpdateError("Resource is not exist.")
        if objectid != blob.hexsha:
            raise CanNotUpdateError("Resource is already updated.")
    cloned_repository_path = mkdtemp()
    repo = _get_repo(project, repository).clone(cloned_repository_path)
    try:
        repo.git.checkout("-b", rev, 'remotes/origin/{0}'.format(rev))
    except GitCommandError:
        pass  # branch already exists, maybe 'master'
    with open(os.path.join(cloned_repository_path, path), 'w') as f:
        f.write(content.encode('utf-8'))
    repo.git.add('-A')
    try:
        if not message:
            message = Config.DEFAULT_COMMIT_MESSAGE
        repo.git.commit('-m', '{0}'.format(message),
                        '--author',
                        '{0} <{1}>'.format(Config.SYSTEM_AUTHOR,
                                           Config.SYSTEM_MAILADDRESS))
        repo.git.push(_get_repository_path(project, repository), rev)
    except Exception:
        raise UnignorableError("Unexpected error. Debug is required.")
    rmtree(cloned_repository_path)


def create_repository(project, repository, username, readme=None):
    path = _get_repository_path(project, repository)
    repo = Repo.init(path, bare=True)
    if not readme:
        readme = Config.DEFAULT_README
    update_resource(project, repository, 'master', 'README', readme,
                    Config.CREATE_MESSAGE)
    uid = getpwnam(username)[2]
    gid = getgrnam(Config.USER_GROUP)[2]
    for root, dirs, files in os.walk(path):
        for d in dirs:
            os.chown(os.path.join(root, d), uid, gid)
            os.chmod(os.path.join(root, d), 0770)
        for f in files:
            os.chown(os.path.join(root, f), uid, gid)
            os.chmod(os.path.join(root, f), 0660)


def create_project(project, username):
    path = _get_project_path(project)
    os.mkdir(path)
    uid = getpwnam(username)[2]
    gid = getgrnam(Config.USER_GROUP)[2]
    os.chown(path, uid, gid)
    os.chmod(path, 0770)


def _get_ref(project, repository, ref, offset=0, limit=100):
    return {'host': Config.HOST,
            'name': repository,
            'path': '/'.join([project, repository]),
            ref: [{'name': r.name,
                   'path': r.name,
                   'timestamp': r.commit.committed_date,
                   'author': r.commit.author.name,
                   'message': r.commit.message}
                  for r in _get_repo(
                      project, repository).__getattribute__(ref)[offset:limit]
                  ]}


def _get_commit(project, repository, rev):
    repo = _get_repo(project, repository)
    try:
        return repo.commit(rev)
    except BadObject:
        raise NotFoundError("rev is invalid: {0}".format(rev))


def _get_repo(project, repository):
    try:
        return Repo(_get_repository_path(project, repository))
    except NoSuchPathError:
        raise NotFoundError("repository is not found: {0}".format(repository))


def _get_repository_path(project, repository):
    return '{0}.git'.format(
        os.path.join(_get_project_path(project), repository))


def _get_project_path(project):
    path = os.path.join(Config.PROJECT_ROOT, project)
    if not path:
        raise NotFoundError("project is not found: {0}".format(project))
    return path


def _commitdata(commit):
    return {'commit': commit.hexsha,
            'parent': [c.hexsha for c in commit.parents],
            'timestamp': commit.committed_date,
            'author': commit.author.name,
            'message': commit.message}


def _blobdata(blob, commit, rev):
    return {'name': blob.name,
            'path': '/'.join([rev, blob.path]),
            'type': 'blob',
            'timestamp': commit.committed_date,
            'author': commit.author.name,
            'message': commit.message}


class NotFoundError(Exception):
    pass


class CanNotUpdateError(Exception):
    pass


class UnignorableError(Exception):
    pass
