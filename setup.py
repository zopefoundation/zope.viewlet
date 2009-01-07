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

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.viewlet',
      version = '3.5.0dev',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Zope Viewlets',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '**********************\n\n'
          + '\n\n' +
          read('src', 'zope', 'viewlet', 'README.txt')
          + '\n\n' +
          read('src', 'zope', 'viewlet', 'directives.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 web html ui viewlet pattern",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://cheeseshop.python.org/pypi/zope.viewlet',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require = dict(
          test=['zope.app.testing',
                'zope.testing',
                'zope.app.securitypolicy',
                'zope.app.zcmlfiles']),
      install_requires=[
          'setuptools',
          'zope.app.pagetemplate',
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
