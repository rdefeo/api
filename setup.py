__author__ = 'robdefeo'
from distutils.core import setup
import os
from setuptools import setup
from api import __version__

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='api',
    version=__version__,
    packages=[
        'api',
        'api.handlers'
    ],
    install_requires=required
)
