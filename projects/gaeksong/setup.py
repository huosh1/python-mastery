#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation pour Gaeksong
"""

from setuptools import setup, find_packages
import os

# Lecture du fichier README pour la description longue
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Outil de reconnaissance active et passive pour la cybersécurité"

# Lecture des requirements
def read_requirements():
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return ['python-whois>=0.8.0', 'dnspython>=2.4.2', 'requests>=2.31.0']

setup(
    name='gaeksong',
    version='1.0.0',
    author='huoshi',
    author_email='huoshi1@proton.me',
    description='Outil de reconnaissance active et passive pour la cybersécurité',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/huosh1/gaeksong',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'gaeksong=gaeksong:main',
        ],
    },
    include_package_data=True,
    package_data={
        'gaeksong': [
            'wordlists/*.txt',
            'templates/*.html',
        ],
    },
    keywords='cybersecurity, reconnaissance, penetration-testing, network-security, osint',
    project_urls={
        'Bug Reports': 'https://github.com/huosh1/gaeksong/issues',
        'Source': 'https://github.com/huosh1/gaeksong',
        'Documentation': 'https://github.com/huosh1/gaeksong/wiki',
    },
)