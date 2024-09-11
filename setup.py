#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

# Fetch the version
exec(open('wrench/version.py').read())

setup(
    name='wrench-api',
    version=str(__version__),
    license='GPLv3',
    author='WRENCH team',
    author_email='support@wrench-project.org',
    description='A Python API for the WRENCH simulation framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wrench-project/wrench-api',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests'
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Topic :: Documentation :: Sphinx',
        'Topic :: System :: Distributed Computing'
    ],
    python_requires='>=3.6'
)
