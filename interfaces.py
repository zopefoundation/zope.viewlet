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
"""Viewlet interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.schema
from zope.app.i18n import ZopeMessageIDFactory as _

from zope.contentprovider.interfaces import IContentProvider


class IViewlet(IContentProvider):
    """A content provider that is managed by another content provider, known
    as viewlet manager.
    """


class IViewletManager(IContentProvider, IReadMapping):
    """An object that provides access to the content providers.

    The viewlet manager's resposibilities are:

      (1) Aggregation of all viewlets of a given type.

      (2) Apply a set of filters to determine the availability of the
          viewlets.

      (3) Sort the viewlets based on some implemented policy.
    """

    providerType = zope.interface.Attribute(
        '''The specific type of provider that are displayed by this manager.''')


class IWeightSupport(zope.interface.Interface):
    """Components implementing this interface are sortable by weight."""

    weight = zope.schema.Int(
        title=_(u'weight'),
        description=_(u"""
            Key for sorting viewlets if the viewlet manager is supporting this
            sort mechanism."""),
        required=False,
        default=0)
