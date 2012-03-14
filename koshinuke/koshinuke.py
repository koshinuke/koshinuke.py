# -*- coding: utf-8 -*-
"""
    koshinuke.koshinuke
    ~~~~~~~~~~~~~~~~~~~

    Implements the routing layer, and acts as controller.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

from functools import wraps
import hashlib
import json
import logging
from logging import FileHandler
import os
import random
import re

from flask import (Flask, request, render_template, abort, redirect, url_for,
                   session)
from flaskext.kvsession import KVSessionExtension
from simplekv.memory import DictStore
from werkzeug import SharedDataMiddleware

from config import Config
import core
from core import NotFoundError, CanNotUpdateError
from auth import authenticate

app = Flask(__name__)

store = DictStore()
KVSessionExtension(store, app)


# configuration
app.config.from_object(Config)


# logger setting
handler = FileHandler(app.config['LOGFILE'], encoding='utf-8')
handler.setLevel(logging.__getattribute__(app.config['LOGLEVEL']))
app.logger.addHandler(handler)


# constants and helper functions
_MAX_CSRF_KEY = 18446744073709551616L
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange


API_VERSION = '1.0'


def jsonify(data):
    return json.dumps(data, ensure_ascii=False)


def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner


def generate_csrf_token():
    # see Flask-SeaSurf http://packages.python.org/Flask-SeaSurf/
    salt = (randrange(0, _MAX_CSRF_KEY), Config.SECRET_KEY)
    return str(hashlib.sha1('{0}{1}'.format(*salt)).hexdigest())


def get_initial_resources():
    resources = []
    for project in core.get_projects():
        for repository in core.get_repositories(project):
            resource = {}
            resource.update(core.get_branches(project, repository))
            resource.update(core.get_tags(project, repository))
            resources.append(resource)
    return resources


@app.before_request
def before_request():
    if not app.testing:
        app.logger.info("access {0} from {1}".format(request.url,
                                                     request.remote_addr))


@app.after_request
def after_request(response):
    response.headers['Server'] = 'I am koshinuke !'
    return response


@app.route('/')
def index():
    if not 'username' in session:
        return redirect(url_for('login'))
    csrf_token = generate_csrf_token()
    session['csrf_token'] = csrf_token
    return render_template('repos.html',
                           csrf=csrf_token, name=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        csrf_token = generate_csrf_token()
        session['csrf_token'] = csrf_token
        return render_template('login.html', csrf=csrf_token)
    else:
        csrf_token = request.form.get('t')
        if not 'csrf_token' in session or csrf_token != session['csrf_token']:
            abort(400)
        username = request.form.get('u')
        password = request.form.get('p')
        if authenticate(username, password):
            session.regenerate()
            session['username'] = username
        return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    session.destroy()
    return redirect(url_for('index'))


@app.route('/api/{0}/'.format(API_VERSION), methods=['GET', 'POST'])
@login_required
def dynamic():
    if request.method == 'GET':
        if request.headers['Accept'] == 'application/json':
            return jsonify(get_initial_resources())
        else:
            return redirect(url_for('index'))
    else:  # create initial repository.
        if not 'X-KoshiNuke' in request.headers or \
           request.headers['X-KoshiNuke'] != session['csrf_token']:
            abort(400)
        mode = request.form.get('!')
        if mode == 'init':
            project_and_repo_name = request.form.get('rn')
            readme = request.form.get('rr')

            separator = project_and_repo_name.find('/')
            project = project_and_repo_name[:separator]
            repository = project_and_repo_name[separator + 1:]
            username = session['username']

            core.create_project(project, username)
            core.create_repository(project, repository, username, readme)
        else:  # mode == 'clone'
            repo_uri = request.form.get('uri')
            repo_username = request.form.get('un')
            repo_password = request.form.get('up')

            username = session['username']
            
            core.clone_remote_repository(repo_uri,
                                         repo_username, repo_password,
                                         username)
        return jsonify(get_initial_resources())


@app.route('/api/{0}/<project>/<repository>/branches'.format(API_VERSION))
@login_required
def branches(project, repository):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(core.get_branches(project, repository, offset, limit))


@app.route('/api/{0}/<project>/<repository>/tags'.format(API_VERSION))
@login_required
def tags(project, repository):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(core.get_tags(project, repository, offset, limit))


@app.route('/api/{0}/<project>/<repository>/tree/<rev>'.format(API_VERSION))
@login_required
def tree_root(project, repository, rev):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(core.get_resources(project, repository, rev, '',
                                      offset, limit))


@app.route('/api/{0}/<project>/<repository>/tree/<rev>/<path:path>'\
           .format(API_VERSION))
@login_required
def tree(project, repository, rev, path):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(core.get_resources(project, repository, rev, path,
                                      offset, limit))


@app.route('/api/{0}/<project>/<repository>/blob/<rev>/<path:path>'\
           .format(API_VERSION),
           methods=['GET', 'POST'])
@login_required
def blob(project, repository, rev, path):
    if request.method == 'POST':
        data = json.loads(request.data)
        objectid = data.get('objectid')
        content = data.get('content')
        message = data.get('message')
        core.update_resource(project, repository, rev, path,
                             content, message, objectid)
    return jsonify(core.get_resource(project, repository, rev, path))


@app.route('/api/{0}/<project>/<repository>/history'.format(API_VERSION))
@login_required
def history(project, repository):
    return jsonify(core.get_history(project, repository))


@app.route('/api/{0}/<project>/<repository>/commits/<ref>'.format(API_VERSION))
@login_required
def commits_root(project, repository, ref):
    rev = request.args.get('commit', None)
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 30, type=int)
    return jsonify(core.get_commits(project, repository, ref, rev,
                                    offset=offset, limit=limit))


@app.route('/api/{0}/<project>/<repository>/commits/<ref>/<path:path>'\
           .format(API_VERSION))
@login_required
def commits(project, repository, ref, path):
    rev = request.args.get('commit', None)
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 30, type=int)
    return jsonify(core.get_commits(project, repository, ref, rev, path,
                                    offset=offset, limit=limit))


@app.route('/api/{0}/<project>/<repository>/commit/<rev>'.format(API_VERSION))
@login_required
def commit(project, repository, rev):
    return jsonify(core.get_commit(project, repository, rev))


@app.route('/api/{0}/<project>/<repository>/blame/<rev>/<path:path>'\
           .format(API_VERSION))
@login_required
def blame(project, repository, rev, path):
    return jsonify(core.get_blame(project, repository, rev, path))


@app.errorhandler(500)
def exception_handler(error):
    # todo: return custom error page
    if isinstance(error, NotFoundError):
        return "Not found.", 404
    elif isinstance(error, CanNotUpdateError):
        return "Resource is already updated.", 409
    app.logger.exception("An internal server error occurred.")
    return "Server error occurred.", 500


# todo: I need favicon!
#@app.route('/favicon.ico')
#def favicon():
#    return app.send_static_file('favicon.ico')


if __name__ == '__main__':
    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app, {'/': os.path.join(os.path.dirname(__file__), 'static')})
    app.run(app.config['HOST'], app.config['PORT'])
