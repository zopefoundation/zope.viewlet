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

import unittest
import zope.interface
import zope.security
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite, DocFileSuite
from zope.app.testing import setup, ztapi

class TestParticipation(object):
    principal = 'foobar'
    interaction = None

def setUp(test):
    setup.placefulSetUp()

    # resource namespace setup
    from zope.app.traversing.interfaces import ITraversable
    from zope.app.traversing.namespace import resource
    ztapi.provideAdapter(None, ITraversable, resource, name="resource")
    ztapi.provideView(None, None, ITraversable, "resource", resource)

    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

    zope.security.management.getInteraction().add(TestParticipation())

def directivesSetUp(test):
    setUp(test)
    setup.setUpTestAsModule(test, 'zope.viewlet.directives')


def tearDown(test):
    setup.placefulTearDown()

def directivesTearDown(test):
    tearDown(test)
    setup.tearDownTestAsModule(test)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('directives.txt',
                     setUp=directivesSetUp, tearDown=directivesTearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
