from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.PloneHelpCenter.config import *
from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def registerNavigationTreeSettings(self, out):
    data = ['HelpCenterHowTo','HelpCenterTutorial']
    pp=getToolByName(self,'portal_properties')
    p = getattr(pp , 'navtree_properties', None)
    mdntl = list(p.getProperty('metaTypesNotToList', []))
    if not mdntl:
        p._setProperty('metaTypesNotToList', data)
    else:
        for t in data:
            if t not in mdntl:
                mdntl.append(t)
        p._updateProperty('metaTypesNotToList', mdntl)

def install(self):
    out = StringIO()

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)

    #register the folderish items in portal_properties/site_properties
    site_props = getToolByName(self, 'portal_properties').site_properties
    use_folder_tabs = site_props.getProperty('use_folder_tabs', None)
    if not 'HelpCenterFAQFolder' in use_folder_tabs:
        site_props._updateProperty('use_folder_tabs', tuple(use_folder_tabs) +
	                               ('HelpCenterFAQFolder',))
        print >> out, "Added HelpCenterFAQFolder to portal_properties/site_properties/use_folder_tabs"

    registerNavigationTreeSettings(self, out)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

