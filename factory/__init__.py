"""
$Id: __init__.py,v 1.1 2005/02/28 05:10:37 limi Exp $

"""

# XXX: This code is not being used at this time.

from Products.Archetypes.Registry import Registry

class Factory:
    """A very abstract factory that doesn't do anything."""

    def __init__(self, name='', description=''):
        if not name:
            name = self.__class__.__name__.title()
        if not description:
            description = getattr(self.__class__, '__doc__')
        self.name = name
        self.description = description

    def __call__(self, context):
        """Here you can do as you wish, but you need
        to make sure that your factory will be called
        more than once (eg: when someone changes settings),
        so you need to check for it and shortcut."""
        pass

factoryRegistry = Registry(allowed_class=Factory)
registerFactory = factoryRegistry.register
getFactory = factoryRegistry.get

class DocFactory(Factory):
    """Create a documentation area"""

    def __call__(self, context):
        if not 'documentation' in context.objectIds():
            context.invokeFactory(type_name='Folder',
                                  id='documentation',
                                  title='Documentation',
                                  description='Documentation for ' + context.Title())

registerFactory('documentation', DocFactory())
