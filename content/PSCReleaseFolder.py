"""
$Id: PSCReleaseFolder.py,v 1.1 2005/02/28 05:10:36 limi Exp $
"""

from Products.Archetypes.public import OrderedBaseFolder
from Products.Archetypes.public import registerType
from Products.Archetypes.public import DisplayList

from Products.PloneSoftwareCenter.config import *
from Products.PloneSoftwareCenter.utils import folder_modify_fti

from Products.CMFCore import CMFCorePermissions

from schemata import PSCReleaseFolderSchema

from AccessControl import ClassSecurityInfo

class PSCReleaseFolder(OrderedBaseFolder):
    """ Folder type for holding releases. """

    __implements__ = (OrderedBaseFolder.__implements__,)

    archetype_name = 'Releases Section'
    immediate_view = default_view = 'psc_releasefolder_view'
    content_icon = 'download_icon.gif'
    schema = PSCReleaseFolderSchema

    typeDescription= 'A Releases Section is used to hold software releases. It is given a default short name and title to ensure that projects are consistent. Please do not rename it.'
    typeDescMsgId  = 'description_edit_releasefolder'

    security = ClassSecurityInfo ()

    allowed_content_types=('PSCRelease',)
    filter_content_types=1
    global_allow=0
    
    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/psc_releasefolder_view',
        'permissions' : (CMFCorePermissions.View,)
         },{
        'id'          : 'sharing',
        'name'        : 'Sharing',
        'action'      : 'string:${object_url}/folder_localrole_form',
        'permissions' : (CMFCorePermissions.ManageProperties,)
        }
         )


    security.declareProtected (ADD_CONTENT_PERMISSION, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        """Override for the .py script in portal_scripts with the same name.
        Gives some default names for contained content types:
        """
                        
        # Generate a fake version number, to signify that the user needs to
        # correct it
        
        # find the highest-used major version
        ids = self.objectIds()

        def getMajor(i):
            try:
                return int(float(i))
            except ValueError:
                return 0
        def getMinor(i):
            if "." in i:
                try:
                    return int(float(i[i.find('.')+1:]))
                except ValueError:
                    return 0

        majors, minors = ( [ getMajor(id) for id in ids ],
                           [ getMinor(id) for id in ids ], )

        
        if majors:
            major =  max(majors) or 1
        else: 
            major = 1

        if minors:
            minor = max(minors)
        else:
            minor = 0

        
        while "%s.%s" % (major, minor,) in self.objectIds ():
            minor += 1
        return "%s.%s" % (major, minor,)

registerType(PSCReleaseFolder, PROJECTNAME)
