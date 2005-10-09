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
"""Content Provider Manager implementation

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.security
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.viewlet import interfaces


class ViewletManagerBase(object):
    """The Viewlet Manager Base

    A generic manager class which can be instantiated 
    """
    zope.interface.implements(interfaces.IViewletManager)

    providerType = None

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view


    def __getitem__(self, name):
        """See zope.interface.common.mapping.IReadMapping"""
        # Find the content provider
        provider = zope.component.queryMultiAdapter(
            (self.context, self.request, self.view), self.providerType,
            name=name)

        # If the content provider was not found, then raise a lookup error
        if provider is None:
            raise zope.component.interfaces.ComponentLookupError(
                'No provider with name `%s` found.' %name)

        # If the content provider cannot be accessed, then raise an
        # unauthorized error
        if not zope.security.canAccess(provider, '__call__'):
            raise zope.security.interfaces.Unauthorized(
                'You are not authorized to access the provider '
                'called `%s`.' %name)

        # Return the rendered content provider.
        return provider


    def get(self, name, default=None):
        try:
            return self[name]
        except (zope.component.interfaces.ComponentLookupError,
                zope.security.interfaces.Unauthorized):
            return default


    def __call__(self, *args, **kw):
        """See zope.contentprovider.interfaces.IContentProvider"""

        # Find all content providers for the region
        viewlets = zope.component.getAdapters(
            (self.context, self.request, self.view), self.providerType)

        # Sort out all content providers that cannot be accessed by the
        # principal
        viewlets = [viewlet for name, viewlet in viewlets
                    if zope.security.canAccess(viewlet, '__call__')]

        # Sort the content providers by weight.
        if self.providerType.extends(interfaces.IWeightSupport):
            viewlets.sort(lambda x, y: cmp(x.weight, y.weight))
        else:
            viewlets.sort()

        # Now render the view
        if self.template:
            return self.template(viewlets=viewlets)
        else:
            return u'\n'.join([viewlet() for viewlet in viewlets])


def ViewletManager(providerType, template=None):

    if template is not None:
        template = ViewPageTemplateFile(template)

    return type('<ViewletManager for %s>' %providerType.getName(),
                (ViewletManagerBase,),
                {'providerType': providerType, 'template': template})
