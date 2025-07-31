#!/usr/bin/env python3
"""
Setup script for Gieokja
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

# Lire les requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='gieokja',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Un compagnon CLI intelligent pour la documentation automatique de vos sessions CTF',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/gieokja',
    
    packages=find_packages(),
    
    install_requires=requirements,
    
    entry_points={
        'console_scripts': [
            'gieokja=gieokja:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: System :: Systems Administration',
        'Topic :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Environment :: Console',
    ],
    
    python_requires='>=3.7',
    
    include_package_data=True,
    package_data={
        'gieokja': [
            'templates/*.tpl',
            'config.ini',
        ],
    },
    
    keywords='ctf documentation pentesting security hacking tryhackme hackthebox',
)