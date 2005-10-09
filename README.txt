=============================
Viewlets and Viewlet Managers
=============================

Let's start with some motivation. Using content providers allows us to insert
one piece of HTML content. In most Web development, however, you are often
interested in defining some sort of region and then allow developers to
register content for those regions.

  >>> from zope.viewlet import interfaces


The Viewlet Manager
-------------------

In this implementation of viewlets, those regions are just content providers
called viewlet managers that manage a special type of content providers known
as viewlets. Every viewlet manager handles the viewlets registered for it:

  >>> class ILeftColumn(interfaces.IViewletManager):
  ...     """Viewlet manager located in the left column."""

You can then create a viewlet manager using this interface now:

  >>> from zope.viewlet import manager
  >>> LeftColumn = manager.ViewletManager(ILeftColumn)

Now we have to instantiate it:

  >>> import zope.interface
  >>> class Content(object):
  ...     zope.interface.implements(zope.interface.Interface)
  >>> content = Content()

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zope.app.publisher.interfaces.browser import IBrowserView
  >>> class View(object):
  ...     zope.interface.implements(IBrowserView)
  ...     def __init__(self, context, request):
  ...         pass
  >>> view = View(content, request)

  >>> leftColumn = LeftColumn(content, request, view)

So initially nothing gets rendered:

  >>> leftColumn()
  u''

But now we register some viewlets for the manager

  >>> import zope.component
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer

  >>> class WeatherBox(object):
  ...     zope.interface.implements(interfaces.IViewlet)
  ...
  ...     def __init__(self, context, request, view, manager):
  ...         pass
  ...
  ...     def __call__(self):
  ...         return u'<div class="box">It is sunny today!</div>'

  # Create a security checker for viewlets.
  >>> from zope.security.checker import NamesChecker, defineChecker
  >>> viewletChecker = NamesChecker(('__call__', 'weight'))
  >>> defineChecker(WeatherBox, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     WeatherBox,
  ...     (zope.interface.Interface, IDefaultBrowserLayer,
  ...     IBrowserView, ILeftColumn),
  ...     interfaces.IViewlet, name='weather')

  >>> class SportBox(object):
  ...     zope.interface.implements(interfaces.IViewlet)
  ...
  ...     def __init__(self, context, request, view, manager):
  ...         pass
  ...
  ...     def __call__(self):
  ...         return u'<div class="box">Patriots (23) : Steelers (7)</div>'

  >>> defineChecker(SportBox, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     SportBox,
  ...     (zope.interface.Interface, IDefaultBrowserLayer,
  ...      IBrowserView, ILeftColumn),
  ...     interfaces.IViewlet, name='sport')

and thus the left column is filled:

  >>> print leftColumn()
  <div class="box">Patriots (23) : Steelers (7)</div>
  <div class="box">It is sunny today!</div>

But this is of course pretty lame, since there is no way of specifying how the
viewlets are put together. But we have a solution. The second argument of the
``ViewletManager()`` function is a template in which we can specify how the
viewlets are put together:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> leftColTemplate = os.path.join(temp_dir, 'leftCol.pt')
  >>> open(leftColTemplate, 'w').write('''
  ... <div class="left-column">
  ...   <tal:block repeat="viewlet options/viewlets"
  ...              replace="structure viewlet" />
  ... </div>
  ... ''')

  >>> LeftColumn = manager.ViewletManager(ILeftColumn, template=leftColTemplate)
  >>> leftColumn = LeftColumn(content, request, view)

XXX: Fix this silly thing; viewlets should be directly available.

As you can see, the viewlet manager provides a global ``options/viewlets``
variable that is an iterable of all the avialable viewlets in the correct
order:

  >>> print leftColumn().strip()
  <div class="left-column">
    <div class="box">Patriots (23) : Steelers (7)</div>
    <div class="box">It is sunny today!</div>
  </div>

You can also lookup the viewlets directly for management purposes:

  >>> leftColumn['weather']
  <WeatherBox ...>
  >>> leftColumn.get('weather')
  <WeatherBox ...>

If the viewlet is not found, then the expected behavior is provided:

  >>> leftColumn['stock']
  Traceback (most recent call last):
  ...
  ComponentLookupError: 'No provider with name `stock` found.'

  >>> leftColumn.get('stock') is None
  True

Customizing the default Viewlet Manager
---------------------------------------

One important feature of any viewlet manager is to be able to filter and sort
the viewlets it is displaying. The default viewlet manager that we have been
using in the tests above, supports filtering by access availability and
sorting via the viewlet's ``__cmp__()`` method (default). You can easily
override this default policy by providing a base viewlet manager class.

In our case we will manage the viewlets using a global list:

  >>> shown = ['weather', 'sport']

The viewlet manager base class now uses this list:

  >>> class ListViewletManager(object):
  ...
  ...     def filter(self, viewlets):
  ...         viewlets = super(ListViewletManager, self).filter(viewlets)
  ...         return [(name, viewlet)
  ...                 for name, viewlet in viewlets
  ...                 if name in shown]
  ...
  ...     def sort(self, viewlets):
  ...         viewlets = dict(viewlets)
  ...         return [(name, viewlets[name]) for name in shown]

Let's now create a new viewlet manager:

  >>> LeftColumn = manager.ViewletManager(
  ...     ILeftColumn, bases=(ListViewletManager,), template=leftColTemplate)
  >>> leftColumn = LeftColumn(content, request, view)

So we get the weather box first and the sport box second:

  >>> print leftColumn().strip()
  <div class="left-column">
    <div class="box">It is sunny today!</div>
    <div class="box">Patriots (23) : Steelers (7)</div>
  </div>

Now let's change the order...

  >>> shown.reverse()

and the order should switch as well:

  >>> print leftColumn().strip()
  <div class="left-column">
    <div class="box">Patriots (23) : Steelers (7)</div>
    <div class="box">It is sunny today!</div>
  </div>

Of course, we also can remove a shown viewlet:

  >>> weather = shown.pop()
  >>> print leftColumn().strip()
  <div class="left-column">
    <div class="box">Patriots (23) : Steelers (7)</div>
  </div>


Viewlet Base Classes
--------------------


A Complex Example
-----------------

So far we have only demonstrated simple (maybe overly trivial) use cases of
the viewlet system. In the following example, we are going to develop a
generic contents view for files. The step is to create a file component:

  >>> class IFile(zope.interface.Interface):
  ...     data = zope.interface.Attribute('Data of file.')

  >>> class File(object):
  ...     zope.interface.implements(IFile)
  ...     def __init__(self, data=''):
  ...         self.__name__ = ''
  ...         self.data = data

Since we want to also provide the size of a file, here a simple implementation
of the ``ISized`` interface:

  >>> from zope.app import size
  >>> class FileSized(object):
  ...     zope.interface.implements(size.interfaces.ISized)
  ...     zope.component.adapts(IFile)
  ...
  ...     def __init__(self, file):
  ...         self.file = file
  ...
  ...     def sizeForSorting(self):
  ...         return 'byte', len(self.file.data)
  ...
  ...     def sizeForDisplay(self):
  ...         return '%i bytes' %len(self.file.data)

  >>> zope.component.provideAdapter(FileSized)

We also need a container to which we can add files:

  >>> class Container(dict):
  ...     def __setitem__(self, name, value):
  ...         value.__name__ = name
  ...         super(Container, self).__setitem__(name, value)

Here is some sample data:

  >>> container = Container()
  >>> container['test.txt'] = File('Hello World!')
  >>> container['mypage.html'] = File('<html><body>Hello World!</body></html>')
  >>> container['data.xml'] = File('<message>Hello World!</message>')

The contents view of the container should iterate through the container and
represent the files in a table:

  >>> contentsTemplate = os.path.join(temp_dir, 'contents.pt')
  >>> open(contentsTemplate, 'w').write('''
  ... <html>
  ...   <body>
  ...     <h1>Cotnents</h1>
  ...     <div tal:content="structure provider:contents" />
  ...   </body>
  ... </html>
  ... ''')

  >>> from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
  >>> Contents = SimpleViewClass(contentsTemplate, name='contents.html')


Now we have to write our own viewlet manager. In this case we cannot use the
default implementation, since the viewlets will be looked up for each
different item:

  >>> shownColumns = []

  >>> class ContentsViewletManager(object):
  ...     index = None
  ...
  ...     def __init__(self, context, request, view):
  ...         self.context = context
  ...         self.request = request
  ...         self.view = view
  ...
  ...     def rows(self):
  ...         rows = []
  ...         for name, value in self.context.items():
  ...             rows.append(
  ...                 [zope.component.getMultiAdapter(
  ...                     (value, self.request, self.view, self),
  ...                     interfaces.IViewlet, name=colname)
  ...                  for colname in shownColumns])
  ...         return rows
  ...
  ...     def __call__(self, *args, **kw):
  ...         return self.index(*args, **kw)

Now we need a template to produce the contents table:

  >>> tableTemplate = os.path.join(temp_dir, 'table.pt')
  >>> open(tableTemplate, 'w').write('''
  ... <table>
  ...   <tr tal:repeat="row view/rows">
  ...     <td tal:repeat="column row">
  ...       <tal:block replace="structure column" />
  ...     </td>
  ...   </tr>
  ... </table>
  ... ''')

From the two pieces above, we can generate the final viewlet manager class and
register it (it's a bit tedious, I know):

  >>> from zope.app.pagetemplate.viewpagetemplatefile import \
  ...     ViewPageTemplateFile
  >>> ContentsViewletManager = type(
  ...     'ContentsViewletManager', (ContentsViewletManager,),
  ...     {'index': ViewPageTemplateFile(tableTemplate)})

  >>> zope.component.provideAdapter(
  ...     ContentsViewletManager,
  ...     (Container, IDefaultBrowserLayer, zope.interface.Interface),
  ...     interfaces.IViewletManager,name='contents')

Since we have not defined any viewlets yet, the table is totally empty:

  >>> contents = Contents(container, request)
  >>> print contents().strip()
  <html>
    <body>
      <h1>Cotnents</h1>
      <div>
        <table>
          <tr>
          </tr>
          <tr>
          </tr>
          <tr>
          </tr>
        </table>
      </div>
    </body>
  </html>

Now let's create a first viewlet for the manager...

  >>> class NameViewlet(object):
  ...
  ...     def __init__(self, context, request, view, manager):
  ...         self.context = context
  ...
  ...     def __call__(self):
  ...         return self.context.__name__

and register it:

  >>> zope.component.provideAdapter(
  ...     NameViewlet,
  ...     (IFile, IDefaultBrowserLayer,
  ...      zope.interface.Interface, ContentsViewletManager),
  ...     interfaces.IViewlet, name='name')

Note how you register the viewlet on ``IFile`` and not on the container. Now
we should be able to see the name for each file in the container:

  >>> print contents().strip()
  <html>
    <body>
      <h1>Cotnents</h1>
      <div>
        <table>
          <tr>
          </tr>
          <tr>
          </tr>
          <tr>
          </tr>
        </table>
      </div>
    </body>
  </html>

Waaa, nothing there! What happened? Well, we have to tell our user preferences
that we want to see the name as a column in the table:

  >>> shownColumns = ['name']

  >>> print contents().strip()
  <html>
    <body>
      <h1>Cotnents</h1>
      <div>
  <table>
    <tr>
      <td>
        mypage.html
      </td>
    </tr>
    <tr>
      <td>
        data.xml
      </td>
    </tr>
    <tr>
      <td>
        test.txt
      </td>
    </tr>
  </table>
  </div>
    </body>
  </html>



#
#Viewlet
#~~~~~~~
#
#Viewlets are snippets of content that can be placed into a region, such as the
#one defined above. As the name suggests, viewlets are views, but they are
#qualified not only by the context object and the request, but also the view
#they appear in. Also, the viewlet must *provide* the region interface it is
#filling; we will demonstrate a more advanced example later, where the purpose
#of this requirement becomes clear.
#
#Like regular views, viewlets can either use page templates to provide content
#or provide a simple ``__call__`` method. For our first viewlet, let's develop
#a more commonly used page-template-driven viewlet:
#
#  >>> import os, tempfile
#  >>> temp_dir = tempfile.mkdtemp()
#
#  >>> viewletFileName = os.path.join(temp_dir, 'viewlet.pt')
#  >>> open(viewletFileName, 'w').write('''
#  ...         <div class="box">
#  ...           <tal:block replace="viewlet/title" />
#  ...         </div>
#  ... ''')
#
#  >>> class ViewletBase(object):
#  ...     def title(self):
#  ...         return 'Viewlet Title'
#
#As you can see, the viewlet Python object is known as ``viewlet`` inside the
#template, while the view object is still available as ``view``. Next we build
#and register the viewlet using a special helper function:
#
#  # Create the viewlet class
#  >>> from zope.viewlet import viewlet
#  >>> Viewlet = viewlet.SimpleViewletClass(
#  ...     viewletFileName, bases=(ViewletBase,), name='viewlet')
#
#  # Generate a viewlet checker
#  >>> from zope.security.checker import NamesChecker, defineChecker
#  >>> viewletChecker = NamesChecker(('__call__', 'weight', 'title',))
#  >>> defineChecker(Viewlet, viewletChecker)
#
#  # Register the viewlet with component architecture
#  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
#  >>> from zope.app.publisher.interfaces.browser import IBrowserView
#  >>> zope.component.provideAdapter(
#  ...     Viewlet,
#  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
#  ...     ILeftColumn,
#  ...     name='viewlet')
#
#As you can see from the security checker registration, a viewlet provides also
#a weight, which acts as a hint to determine the order in which the viewlets of
#a region should be displayed. The view the viewlet is used in can also be
#accessed via the ``view`` attribute of the viewlet class.
#
#
#
#
#An Alternative Content Provider Manager
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#Let's now imagine that we would like to allow the user to choose the columns
#for the contents view. Here it would not be enough to implement a condition as
#part of the viewlet class, since the TD tag appearance is not controlled by
#the viewlet itself. In those cases it is best to implement a custom content
#provider manager that only returns the viewlets that are specified in an
#option:
#
#  >>> showColumns = ['name', 'size']
#
#So our custom content provider manager could look something like this:
#
#  >>> from zope.contentprovider import manager
#  >>> from zope.contentprovider.interfaces import IContentProviderManager
#  >>> class ContentsContentProviderManager(manager.DefaultContentProviderManager):
#  ...
#  ...     def values(self):
#  ...         viewlets = zope.component.getAdapters(
#  ...             (self.context, self.request, self.view), self.region)
#  ...         viewlets = [(name, viewlet) for name, viewlet in viewlets
#  ...                     if name in showColumns]
#  ...         viewlets.sort(lambda x, y: cmp(showColumns.index(x[0]),
#  ...                                        showColumns.index(y[0])))
#  ...         return [viewlet for name, viewlet in viewlets]
#
#We just have to register it as an adapter:
#
#  >>> zope.component.provideAdapter(
#  ...     ContentsContentProviderManager,
#  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView,
#  ...      IObjectInfoColumn),
#  ...     IContentProviderManager)
#
#  >>> view = zope.component.getMultiAdapter(
#  ...     (content, request), name='contents.html')
#  >>> print view().strip()
#  <html>
#    <body>
#      <h1>Contents</h1>
#      <table>
#        <tr>
#          <td><b>README.txt</b></td>
#          <td>1.2kB</td>
#        </tr>
#        <tr>
#          <td><b>logo.png</b></td>
#          <td>100 x 100</td>
#        </tr>
#      </table>
#    </body>
#  </html>
#
#But if I turn the order around,
#
#  >>> showColumns = ['size', 'name']
#
#it will provide the columns in a different order as well:
#
#  >>> print view().strip()
#  <html>
#    <body>
#      <h1>Contents</h1>
#      <table>
#        <tr>
#          <td>1.2kB</td>
#          <td><b>README.txt</b></td>
#        </tr>
#        <tr>
#          <td>100 x 100</td>
#          <td><b>logo.png</b></td>
#        </tr>
#      </table>
#    </body>
#  </html>
#
#On the other hand, it is as easy to remove a column:
#
#  >>> showColumns = ['name']
#  >>> print view().strip()
#  <html>
#    <body>
#      <h1>Contents</h1>
#      <table>
#        <tr>
#          <td><b>README.txt</b></td>
#        </tr>
#        <tr>
#          <td><b>logo.png</b></td>
#        </tr>
#      </table>
#    </body>
#  </html>
#
#

Cleanup
-------

  >>> import shutil
  >>> shutil.rmtree(temp_dir)

