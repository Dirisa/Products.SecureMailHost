from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.PloneHelpCenter.config import *
from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def install(self):
    out = StringIO()

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)

    #register the folderish items in portal_properties/site_properties
    site_props = getToolByName(self, 'portal_properties').site_properties
    use_folder_tabs = site_props.getProperty('use_folder_tabs', None)
    if not 'HelpCenterFaqFolder' in use_folder_tabs:
        site_props._updateProperty('use_folder_tabs', tuple(use_folder_tabs) +
	                               ('HelpCenterFaqFolder',))
        print >> out, "Added HelpCenterFaqFolder to portal_properties/site_properties/use_folder_tabs"

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

