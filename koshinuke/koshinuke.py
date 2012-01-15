# -*- coding: utf-8 -*-
"""
    koshinuke.koshinuke
    ~~~~~~~~~~~~~~~~~~~

    Implements the routing layer, and acts as controller.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import logging
from logging import FileHandler
import os

from flask import (Flask, request, render_template, abort, redirect, url_for,
                   session)
from flaskext.kvsession import KVSessionExtension
from simplekv.memory import DictStore
from werkzeug import SharedDataMiddleware

from config import Config
from core import (get_projects, get_repositories,
                  get_resource, get_resources, get_branches, get_tags,
                  get_history, get_commits, get_commit, update_resource,
                  create_project, create_repository,
                  NotFoundError, CanNotUpdateError)
from auth import authenticate
from utils import jsonify, generate_csrf_token

app = Flask(__name__)

store = DictStore()
KVSessionExtension(store, app)

# configuration
app.config.from_object(Config)

# logger setting
handler = FileHandler(app.config['LOGFILE'], encoding='utf-8')
handler.setLevel(logging.__getattribute__(app.config['LOGLEVEL']))
app.logger.addHandler(handler)


def get_initial_resources():
    resources = []
    for project in get_projects():
        for repository in get_repositories(project):
            resource = {}
            resource.update(get_branches(project, repository))
            resource.update(get_tags(project, repository))
            resources.append(resource)
    return resources


@app.before_request
def before_request():
    # todo: check login
    # todo: check csrf here
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
        csrf_token = generate_csrf_token()
        session['csrf_token'] = csrf_token
        return render_template('login.html', csrf=csrf_token)
    else:
        csrf_token = generate_csrf_token()
        session['csrf_token'] = csrf_token
        return render_template('repos.html',
                               csrf=csrf_token, name=session['username'])


@app.route('/login', methods=['POST'])
def login():
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
def logout():
    session.destroy()
    return redirect(url_for('index'))


@app.route('/dynamic', methods=['POST'])
def init():
    # check login
    if not 'X-KoshiNuke' in request.headers or \
       request.headers['X-KoshiNuke'] != session['csrf_token']:
        abort(400)
    project_and_repo_name = request.form.get('rn')
    readme = request.form.get('rr')

    separator = project_and_repo_name.find('/')
    project = project_and_repo_name[:separator]
    repository = project_and_repo_name[separator + 1:]
    username = session['username']

    create_project(project, username)
    create_repository(project, repository, username, readme)
    return jsonify(get_initial_resources())


@app.route('/dynamic/')
def dynamic():
    if request.headers['Accept'] == 'application/json':
        return jsonify(get_initial_resources())
    else:
        return redirect(url_for('index'))


@app.route('/dynamic/<project>/<repository>/branches')
def branches(project, repository):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_branches(project, repository, offset, limit))


@app.route('/dynamic/<project>/<repository>/tags')
def tags(project, repository):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_tags(project, repository, offset, limit))


@app.route('/dynamic/<project>/<repository>/tree/<rev>')
def tree_root(project, repository, rev):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_resources(project, repository, rev, '', offset, limit))


@app.route('/dynamic/<project>/<repository>/tree/<rev>/<path:path>')
def tree(project, repository, rev, path):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_resources(project, repository, rev, path,
                                 offset, limit))


@app.route('/dynamic/<project>/<repository>/blob/<rev>/<path:path>',
           methods=['GET', 'POST'])
def blob(project, repository, rev, path):
    if request.method == 'GET':
        return jsonify(get_resource(project, repository, rev, path))
    else:
        parent = request.form.get('commit')
        content = request.form.get('content')
        message = request.form.get('message')
        update_resource(project, repository, rev, path,
                        content, message, parent)
        return 'Resouce is updated successfully.', 200


@app.route('/dynamic/<project>/<repository>/history')
def history(project, repository):
    return jsonify(get_history(project, repository))


@app.route('/dynamic/<project>/<repository>/commits/<ref>')
def commits_root(project, repository, ref):
    rev = request.args.get('commit', None)
    limit = request.args.get('limit', 30, type=int)
    return jsonify(get_commits(project, repository, ref, rev, limit=limit))


@app.route('/dynamic/<project>/<repository>/commits/<ref>/<path:path>')
def commits(project, repository, ref, path):
    rev = request.args.get('commit', None)
    limit = request.args.get('limit', 30, type=int)
    return jsonify(get_commits(project, repository, ref, rev,
                               path, limit=limit))


@app.route('/dynamic/<project>/<repository>/commit/<rev>')
def commit(project, repository, rev):
    return jsonify(get_commit(project, repository, rev))


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
