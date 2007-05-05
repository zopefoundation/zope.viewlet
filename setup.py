##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for zope.viewlet package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name='zope.viewlet',
      version = '3.4.0b1',
      url='http://svn.zope.org/zope.viewlet',
      license='ZPL 2.1',
      description='Zope viewlet',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="Viewlets provide a generic framework for"
                       "building pluggable user interfaces.",

      packages=find_packages('src'),
	  package_dir = {'': 'src'},

      namespace_packages=['zope',],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles']),
      install_requires=['setuptools',
                        'zope.app.pagetemplate',
                        'zope.app.publisher',
                        'zope.component',
                        'zope.configuration',
                        'zope.contentprovider',
                        'zope.event',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.location',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.traversing',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
