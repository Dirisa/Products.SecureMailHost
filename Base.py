"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Base.py,v 1.1 2003/11/28 07:32:33 ajung Exp $
"""

from Globals import InitializeClass
from Products.Archetypes.BaseBTreeFolder import BaseBTreeFolder

class Base(BaseBTreeFolder):
    """ base class for collector/issues """

    def SchemataNames(self):
        """ return ordered list of schemata names """
        return [n for n in self.schema.getSchemataNames() if not n in ('default', 'metadata')]
 
    def base_edit(self, RESPONSE):
        """ redirect to our own edit method """
        RESPONSE.redirect('pcng_base_edit')

InitializeClass(Base)
