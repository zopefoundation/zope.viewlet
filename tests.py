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
from zope.app.testing import setup

from zope.viewlet import interfaces


class TestParticipation(object):
    principal = 'foobar'
    interaction = None


class ILeftViewlet(interfaces.IViewlet):
    """Test viewlet type."""


class TestViewlet(object):

    def doSomething(self):
        return u'something'


class TestViewlet2(object):

    def __call__(self):
        return u'called'


def setUp(test):
    setup.placefulSetUp()

    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

    zope.security.management.getInteraction().add(TestParticipation())


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('directives.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
