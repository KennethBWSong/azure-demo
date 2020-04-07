#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from setuptools import setup, find_packages

VERSION = "0.0.1"

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = []

setup(
    name='starter',
    version=VERSION,
    description='Azure starter extension',
    long_description='Help developer quick start on Azure services.',
    license='MIT',
    author='Bowen Song',
    author_email='bowsong@microsoft.com',
    # url='https://github.com/Azure/azure-cli-extensions/tree/master/src/starter',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    package_data={'azext_starter': ['azext_metadata.json']},
    install_requires=DEPENDENCIES
)