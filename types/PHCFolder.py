#
#  This is the Plone Help Center FAQ Folder type, with enhanced features
#  like dividing the FAQ into Sections, and Display relevant
#  versions.
#


from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HCFolderSchemaWithVersion as HCSchema

class PHCFolder:
    """A simple mixin for folderish archetype"""

    typeDescription= 'This is a folder that holds PHC content'
    typeDescMsgId  = 'description_edit_phc'

    content_icon = 'icon.gif'

    schema = HCSchema
    archetype_name = 'PHCFolder'
    meta_type = 'PHCFolder'
    global_allow = 0
    filter_content_types = 1
    
    security = ClassSecurityInfo()

    def _get_versions_vocab(self):
        return self.versions

    def _get_sections_vocab(self):
        return self.sections
        
    def Versions(self):
        """method to display the versions in a nicer way
        """

        # XXX is this really necessary? the widget supports this, doesn't it? ~limi
        result=""
        for version in self.versions:
            if result:
                result=result+", "+ version
            else:
                result=version
        return result

