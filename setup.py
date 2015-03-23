__author__ = 'robdefeo'
from distutils.core import setup
import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='api',
    version='0.0.1',
    packages=[
        'api',
        'api.handlers'
    ],
    install_requires=required
)
