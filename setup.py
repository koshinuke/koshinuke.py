# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

description = ("koshinuke.py is python implementation "
               "of the server side for KoshiNuke.")

cmdclass = {}

from setup_env import EnvBuild
cmdclass['build_env'] = EnvBuild

setup(
    name='koshinuke.py',
    version='0.1.0',
    packages=find_packages(),
    description=description,
    cmdclass=cmdclass,
    install_requires=[
        'setuptools',
        'Flask',
        'Flask-KVSession',
        "GitPython",
    ],
    author='lanius',
    author_email='lanius@nirvake.org',
    license="Apache License 2.0",
)
