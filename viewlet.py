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
"""Viewlet implementation

$Id: metaconfigure.py 38437 2005-09-10 01:59:07Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

import os
import sys
import zope.interface

from zope.app.pagetemplate.simpleviewclass import simple
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.traversing import api

from zope.viewlet import interfaces


class ViewletPageTemplateFile(ViewPageTemplateFile):

    def pt_getContext(self, instance, request, **_kw):
        namespace = super(ViewletPageTemplateFile, self).pt_getContext(
            instance, request, **_kw)
        namespace['view'] = instance.view
        namespace['viewlet'] = instance
        return namespace


class SimpleViewlet(BrowserView):
    """Viewlet adapter class used in meta directive as a mixin class."""

    zope.interface.implements(interfaces.IViewlet)

    def __init__(self, context, request, view, providerType):
        super(SimpleViewlet, self).__init__(context, request)
        self.view = view


class SimpleAttributeViewlet(SimpleViewlet):

    def publishTraverse(self, request, name):
        raise NotFound(self, name, request)

    def __call__(self, *args, **kw):
        # If a class doesn't provide it's own call, then get the attribute
        # given by the browser default.

        attr = self.__page_attribute__
        if attr == '__call__':
            raise AttributeError("__call__")

        meth = getattr(self, attr)
        return meth(*args, **kw)


def SimpleViewletClass(template, offering=None, bases=(), attributes=None,
                       name=u''):
    # Get the current frame
    if offering is None:
        offering = sys._getframe(1).f_globals

    # Create the base class hierarchy
    bases += (SimpleViewlet, simple)

    attrs = {'index' : ViewletPageTemplateFile(template, offering),
             '__name__' : name}
    if attributes:
        attrs.update(attributes)

    # Generate a derived view class.
    class_ = type("SimpleViewletClass from %s" % template, bases, attrs)

    return class_


class ResourceViewletBase(object):

    _path = None

    def getURL(self):
        resource = api.traverse(self.context, '++resource++' + self._path,
                                request=self.request)
        return resource()

    def __call__(self, *args, **kw):
        return self.index(*args, **kw)


def JavaScriptViewlet(path):
    """Create a viewlet that can simply insert a javascript link."""
    src = os.path.join(os.path.dirname(__file__), 'javascript_viewlet.pt')

    klass = type('JavaScriptViewlet',
                 (ResourceViewletBase, SimpleViewlet),
                  {'index': ViewletPageTemplateFile(src),
                   '_path': path})

    return klass


class CSSResourceViewletBase(ResourceViewletBase):

    _media = 'all'
    _rel = 'stylesheet'

    def getMedia(self):
        return self._media

    def getRel(self):
        return self._rel


def CSSViewlet(path, media="all", rel="stylesheet"):
    """Create a viewlet that can simply insert a javascript link."""
    src = os.path.join(os.path.dirname(__file__), 'css_viewlet.pt')

    klass = type('CSSViewlet',
                 (CSSResourceViewletBase, SimpleViewlet),
                  {'index': ViewletPageTemplateFile(src),
                   '_path': path,
                   '_media':media,
                   '_rel':rel})

    return klass

