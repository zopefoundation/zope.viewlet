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
called viewlet managers that manage other content providers known as
viewlets. Every viewlet manager can handle viewlets of a certain type:

  >>> class ILeftColumnViewlet(interfaces.IViewlet):
  ...     """This is a viewlet located in the left column."""

You can then create a viewlet manager for this viewlet type:

  >>> from zope.viewlet import manager
  >>> leftColumn = manager.ViewletManager(ILeftColumnViewlet)

So initially nothing gets rendered:

  >>> leftColumn()
  u''

But now we register some viewlets for the manager

  >>> import zope.component
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.app.publisher.interfaces.browser import IBrowserView

  >>> class WeatherBox(ILeftColumnViewlet):
  ...
  ...     def __init__(self, context, request, view):
  ...         pass
  ...
  ...     def __call__(self):
  ...         return u'<div class="box">It is sunny today!</div>'

  >>> zope.component.provideAdapter(
  ...     WeatherBox,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
  ...     ILeftColumnViewlet, name='weather')

  >>> class SportBox(ILeftColumnViewlet):
  ...
  ...     def __init__(self, context, request, view):
  ...         pass
  ...
  ...     def __call__(self):
  ...         return u'<div class="box">Patriots (23) : Steelers (7)</div>'

  >>> zope.component.provideAdapter(
  ...     SportBox,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
  ...     ILeftColumnViewlet, name='sport')

and thus the left column is filled:

  >>> leftColumn()

But this is of course pretty lame, since there is no way of specifying how the
viewlets are put together. But we have a solution. The second argument of the
``ViewletManager()`` function is a template in which we can specify how the
viewlets are put together:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> leftColTemplate = os.path.join(temp_dir, 'leftCol.pt')
  >>> open(leftColTemplate, 'w').write('''
  ... <div class="left-column">
  ...   <tal:block repeat="viewlet viewlets"
  ...              replace="structure viewlet" />
  ... </div>
  ... ''')

  >>> leftColumn = manager.ViewletManager(ILeftColumnViewlet, leftColTemplate)

As you can see, the viewlet manager provides a global ``viewlets`` variable
that is an iterable of all the avialable viewlets in the correct order:

  >>> leftColumn()

You can also lookup the viewlets directly for management purposes:

  >>> leftColumn['weather']
  <WeatherBox ...>
  >>> leftColumn.get('weather')
  <WeatherBox ...>

If the viewlet is not found, then the expected behavior is provided:

  >>> leftColumn['stock']

  >>> leftColumn.get('stock') is None
  True


Viewlet Weight Support
----------------------


A Complex Example
-----------------

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
#Changing the Weight
#~~~~~~~~~~~~~~~~~~~
#
#Let's ensure that the weight really affects the order of the viewlets. If we
#change the weights around,
#
#  >>> InfoViewlet.weight = 0
#  >>> Viewlet._weight = 1
#
#the order of the left column in the page template should change:
#
#  >>> print view().strip()
#  <html>
#    <body>
#      <h1>My Web Page</h1>
#      <div class="left-column">
#        <div class="column-item">
#          <h3>Some Information.</h3>
#        </div>
#        <div class="column-item">
#  <BLANKLINE>
#          <div class="box">
#            Viewlet Title
#          </div>
#  <BLANKLINE>
#        </div>
#      </div>
#      <div class="main">
#        Content here
#      </div>
#    </body>
#  </html>
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

