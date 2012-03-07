# -*- coding: utf-8 -*-

from grp import getgrnam
import os
from pwd import getpwnam
from shutil import copy, copytree, rmtree
from subprocess import call
import sys
from tempfile import mkdtemp

from setuptools import Command


class KoshinukeBuild(Command):
    description = 'Build the koshinuke environment'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """For Ubuntu."""
        # todo: consider other platforms

        # todo: externalize
        user = 'ubuntu'
        usergroup = 'knusers'
        src_root = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                'koshinuke')
        project_root = '/var/koshinuke'

        uid, gid = getpwnam(user)[2:4]
        
        # Install necessary tools
        print("Install tools.")
        tools = 'git-core', 'subversion'
        for t in tools:
            call(['aptitude', 'install', t, '-y'])

        # Create koshinuke user group
        print("Create group for user.")
        call(['addgroup', usergroup])
        usergroup_gid = getgrnam(usergroup)[2]

        # Create project root
        print("Create project root.")
        if not os.path.exists(project_root):
            os.mkdir(project_root)
        os.chown(project_root, uid, usergroup_gid)

        # Setting chroot for koshinuke users
        print("Setting chroot for users.")
        sshd_config = '/etc/ssh/sshd_config'
        config = ("Match Group {0}\n"
                  "  ChrootDirectory {1}\n".format(usergroup, project_root))
        with open(sshd_config, 'a') as f:
            f.write(config)
        call(['service', 'ssh', 'restart'])

        # Copy bash, git, git-upload-pack, git-receive-pack, 
        # and necessary objects for using git on chroot. 
        # It can be found out by command "ldd \`which git\`" for example
        dirs = [os.path.join('usr', 'bin'), 'lib', 'lib64']
        for d in dirs:
            path = os.path.join(project_root, d)
            if not os.path.exists(path):
                os.makedirs(path)

        copy_target = {
            '/bin': ['bash'],
            '/usr/bin': ['git', 'git-upload-pack', 'git-receive-pack'],
            '/lib': ['libz.so.1', 'libpthread.so.0', 'libpthread.so.0',
                    'libncurses.so.5', 'libdl.so.2', 'libc.so.6'],
            '/lib64': ['ld-linux-x86-64.so.2']
            }
        for d, files in copy_target.items():
            for f in files:
                copy(os.path.join(d, f), os.path.join(project_root, d[1:]))

        # Project root must be owned by root user for chroot. 
        # For this reason,
        # sadly need to use sudo to create koshinuke project later
        root_uid, root_gid = getpwnam('root')[2:4]
        os.chown(project_root, root_uid, root_gid)

        # Download koshinuke client source code and closure-library
        print("Setup client libraries.")
        tmpdir = mkdtemp()
        os.chdir(tmpdir)
        call(['git', 'clone', 'git://github.com/koshinuke/koshinuke.git'])
        os.chdir('koshinuke')
        templates_dir = os.path.join(src_root, 'templates')
        templates = ['login.html', 'repos.html']
        for t in templates:
            copy(t, templates_dir)
        static_dir = os.path.join(src_root, 'static')
        if not os.path.exists(static_dir):
            copytree('static', static_dir)
            os.chdir(static_dir)
            call(['svn', 'co',
                  'http://closure-library.googlecode.com/svn/trunk/',
                  'closure-library', '-q'])
        change_owner(templates_dir, uid, gid)
        change_owner(static_dir, uid, gid)
        rmtree(tmpdir)


def change_owner(path, uid, gid):
    for root, dirs, files in os.walk(path):
        for f in files:
            os.chown(os.path.join(root, f), uid, gid)
        for d in dirs:
            os.chown(os.path.join(root, d), uid, gid)
