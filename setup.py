#!/usr/bin/env python
from setuptools import setup

setup(
    name='filebutler-upload',
    version='0.0.1',
    url='https://github.com/JHaals/filebutler-upload',
    license = 'BSD License',
    author = 'Johan Haals',
    author_email = 'johan.haals@gmail.com',
    description = '',
    packages = ['filebutler_upload'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: File Sharing',
        'Topic :: Utilities',
    ],
    entry_points = {
        'console_scripts': [
            'filebutler = filebutler_upload.main:main'
        ]
    },
)
