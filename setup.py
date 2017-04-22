#!/usr/bin/env python

from setuptools import setup

setup(name='aw-detector',
      version='0.1',
      description='',
      author='Erik Bjäreholt',
      author_email='erik@bjareho.lt',
      url='https://github.com/ActivityWatch/aw-detector',
      packages=['aw_detector'],
      install_requires=[
          'aw-client',
      ],
      dependency_links=[
          'https://github.com/ActivityWatch/aw-client/tarball/master#egg=aw-client'
      ],
      entry_points={
          'console_scripts': ['aw-detector = aw_detector:main']
      },
      classifier=[
          'Programming Language :: Python :: 3'
      ])
