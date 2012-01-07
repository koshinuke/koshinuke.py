# -*- coding: utf-8 -*-
"""
    koshinuke.koshinuke
    ~~~~~~~~~~~~~~~~~~~

    Implements the routing layer, and acts as controller.

    :copyright: (c) 2012 lanius
    :license: Apache License, Version 2.0, see LICENSE for more details.
"""

import json
import logging
from logging import FileHandler
import os

from flask import Flask, request, render_template, abort, redirect, url_for
from flask import session
from werkzeug import SharedDataMiddleware

from config import Config
from core import get_projects, get_repositories
from core import get_resource, get_resources, get_branches, get_tags
from core import get_history, get_commits, get_commit, update_resource
from core import NotFoundError, CanNotUpdateError


app = Flask(__name__)

# configuration
app.config.from_object(Config)

# logger setting
handler = FileHandler(app.config['LOGFILE'], encoding='utf-8')
handler.setLevel(logging.__getattribute__(app.config['LOGLEVEL']))
app.logger.addHandler(handler)


def jsonify(data):
    return json.dumps(data, ensure_ascii=False)


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
    if not request.is_xhr:
        return app.send_static_file('repos.html')
    resources = []
    for project in get_projects():
        for repository in get_repositories(project):
            resource = {}
            resource.update(get_branches(project, repository))
            resource.update(get_tags(project, repository))
            resources.append(resource)
    return jsonify(resources)


@app.route('/<project>/<repository>/branches')
def branches(project, repository):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_branches(project, repository, offset, limit))


@app.route('/<project>/<repository>/tags')
def tags(project, repository):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_tags(project, repository, offset, limit))


@app.route('/<project>/<repository>/tree/<rev>')
def tree_root(project, repository, rev):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_resources(project, repository, rev, '', offset, limit))


@app.route('/<project>/<repository>/tree/<rev>/<path:path>')
def tree(project, repository, rev, path):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_resources(project, repository, rev, path,
                                 offset, limit))


@app.route('/<project>/<repository>/blob/<rev>/<path:path>',
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


@app.route('/<project>/<repository>/history')
def history(project, repository):
    return jsonify(get_history(project, repository))


@app.route('/<project>/<repository>/commits/<ref>')
def commits_root(project, repository, ref):
    rev = request.args.get('commit', None)
    limit = request.args.get('limit', 30, type=int)
    return jsonify(get_commits(project, repository, ref, rev, limit=limit))


@app.route('/<project>/<repository>/commits/<ref>/<path:path>')
def commits(project, repository, ref, path):
    rev = request.args.get('commit', None)
    limit = request.args.get('limit', 30, type=int)
    return jsonify(get_commits(project, repository, ref, rev,
                               path, limit=limit))


@app.route('/<project>/<repository>/commit/<rev>')
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
