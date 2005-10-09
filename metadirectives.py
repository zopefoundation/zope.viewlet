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
"""Viewlet metadirective

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.configuration.fields
import zope.schema

from zope.app.publisher.browser import metadirectives


class IViewletManagerDirective(metadirectives.IPagesDirective):
    """A directive to register a new viewlet manager.

    Viewlet manager registrations are very similar to page registrations, 
    except that they are additionally qualified by a type where is used for
    lookup viewlets of this type.
    """

    providerType = zope.configuration.fields.GlobalInterface(
        title=u"Viewlet type",
        description=u"The type interface for viewlets.",
        required=True)

    name = zope.schema.TextLine(
        title=u"The name of the page (view)",
        description=u"""
        The name shows up in URLs/paths. For example 'foo' or
        'foo.html'. This attribute is required unless you use the
        subdirective 'page' to create sub views. If you do not have
        sub pages, it is common to use an extension for the view name
        such as '.html'. If you do have sub pages and you want to
        provide a view name, you shouldn't use extensions.""",
        required=True)

    template = zope.configuration.fields.Path(
        title=u"The name of a template that implements the page.",
        description=u"""
        Refers to a file containing a page template (should end in
        extension '.pt' or '.html').""",
        required=False)


class IViewletDirective(metadirectives.IPagesDirective,
                        metadirectives.IViewPageSubdirective,
                        IViewletManagerDirective):
    """A directive to register a new viewlet.

    Viewlet registrations are very similar to page registrations, except that
    they are additionally qualified by the region and view they are used for. An
    additional `weight` attribute is specified that is intended to coarsly
    control the order of the viewlets.
    """

    view = zope.configuration.fields.GlobalInterface(
        title=u"view",
        description=u"The interface of the view this viewlet is for. "
                    u"(default IBrowserView)""",
        required=False)

    weight = zope.schema.Int(
        title=u"weight",
        description=u"Integer key for sorting viewlets in the same region.",
        required=False)
