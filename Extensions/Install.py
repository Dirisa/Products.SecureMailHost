from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.PloneLocalFolderNG.config import *

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from types import TupleType
import zLOG

def install(self):
    out = StringIO()
    
    # parentMetaTypesNotToQuery property for portal_properties/navtree_properties
    # must include 'PloneLocalFolderNG' to prevent duplicate folders from being
    # generated in the navtree when a PLFNG object is selected
    url_tool = getToolByName( self, 'portal_url')	
    portal = url_tool.getPortalObject()
    props = portal.portal_properties.navtree_properties
    if props.hasProperty('parentMetaTypesNotToQuery'):
        data = getattr(props, 'parentMetaTypesNotToQuery')
        data = list(data)
        if not 'PloneLocalFolderNG' in data:
             data.append('PloneLocalFolderNG')
             props._updateProperty('parentMetaTypesNotToQuery', data)
             print >> out, "updated parentMetaTypesNotToQuery property with values: %s" % data
        else:
             print >> out, "parentMetaTypesNotToQuery property already includes PloneLocalFolderNG"
    else:
        print >> out, "ERROR: parentMetaTypesNotToQuery property not found!!!"

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

    install_subskin(self, out, GLOBALS)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
