##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Viewlet tests

$Id$
"""
__docformat__ = 'restructuredtext'
import sys
import unittest

import zope.component
from zope.testing import doctest, cleanup
from zope.traversing.testing import setUp as traversingSetUp
from zope.component import eventtesting

def setUp(test):
    cleanup.setUp()
    eventtesting.setUp()
    traversingSetUp()

    # resource namespace setup
    from zope.traversing.interfaces import ITraversable
    from zope.traversing.namespace import resource
    zope.component.provideAdapter(
        resource, (None,), ITraversable, name = "resource")
    zope.component.provideAdapter(
        resource, (None, None), ITraversable, name = "resource")

    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

def tearDown(test):
    cleanup.tearDown()

class FakeModule(object):
    """A fake module."""
    
    def __init__(self, dict):
        self.__dict = dict

    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError(name)

def directivesSetUp(test):
    setUp(test)
    test.globs['__name__'] = 'zope.viewlet.directives'
    sys.modules['zope.viewlet.directives'] = FakeModule(test.globs)

def directivesTearDown(test):
    tearDown(test)
    del sys.modules[test.globs['__name__']]
    test.globs.clear()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        doctest.DocFileSuite('directives.txt',
                     setUp=directivesSetUp, tearDown=directivesTearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')