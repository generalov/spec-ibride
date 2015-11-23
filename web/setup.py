#!/usr/bin/env python

import os
import sys

import versioneer
from setuptools.command.test import test as TestCommand
from setuptools.dist import Distribution

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup, find_packages


class BinaryDistribution(Distribution):

    def is_pure(self):
        # return False if you ship a .so, .dylib or .dll
        # as part of your package data
        return True


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', 'Arguments to pass to tox')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


setup(
    name='spec-ibride',
    version=versioneer.get_version(),
    license='MIT',
    packages=find_packages('', exclude=['tests.*', 'tests']),
    classifiers=['Private :: Do Not Upload'],
    zip_safe=True,
    install_requires=[
        'django',
        'django-tagging',
        'django-favicon',
        'django-debug-toolbar',
        'django-extensions',
        'linaro-django-pagination',
        'django-webpack-loader',
        'IXDjango',
        'mysqlclient',
    ],
    tests_require=['tox'],
    cmdclass=dict(versioneer.get_cmdclass().items(), **{'test': Tox}),
    distclass=BinaryDistribution,
)
