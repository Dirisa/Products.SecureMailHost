import os

from DateTime.DateTime import DateTime
from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.FSObject import FSObject
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField, StringWidget
from Products.Archetypes.public import BaseFolder, registerType
from Products.CMFCore.CMFCorePermissions import *
from config import PROJECTNAME

schema = BaseSchema +  Schema((
    StringField('folder',
                widget=StringWidget(label='Local directory name')
                ),
    ))


class TypeInfo(SimpleItem):

    __allow_acces_to_unprotected_subobjects__ = 1

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess('allow')

    
    immediate_view = 'view'

    def setMimeType(self, mt):
        self.mime_type = mt

    security.declarePublic('getActionById')
    def getActionById(self, id, default=None):
        """ None """
        return None

    security.declarePublic('Title')
    def Title(self):
        """ None """
        return self.mime_type



InitializeClass(TypeInfo)

class FileProxy(FSObject):

    security = ClassSecurityInfo()
    meta_type = 'PloneLocalFolderFileProxy'

    def setMimeType(self, mt):
        self.mime_type = mt

    def setIconPath(self, icon_path):
        self.icon_path = icon_path


    security.declarePublic('title_or_id')
    def title_or_id(self):
        """ return title or id """
        return self.id

    security.declarePublic('getTypeInfo')
    def getTypeInfo(self):
        """ return type info """
        TI = TypeInfo(self.id, self.mime_type)
        TI.setMimeType(self.mime_type)
        return TI

    def _readFile(self, *args, **kw):
        """ read the file """
    
    security.declarePublic('getIcon')
    def getIcon(self, arg):
        """ icon """
        return self.icon_path


    security.declarePublic('ModificationDate')
    def ModificationDate(self):
        """ None """
        return DateTime(os.stat(self._filepath)[8])

    security.declarePublic('get_size')
    def get_size(self):
        """ None """
        return os.stat(self._filepath)[6]

InitializeClass(FileProxy)


class PloneLocalFolderNG(BaseFolder):
    """This is a sample article, it has an overridden view for show,
    but this is purely optional
    """

    schema = schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/plfng_view',
        'permissions': (View,)
        },)

    def listFolderContents(self, contentFilter=None, suppressHiddenFiles=None):
        """ list content of local filesystem """

        l = []
        for f in os.listdir(self.folder):
            P = FileProxy(f, os.path.join(self.folder, f), f)
            mi = self.mimetypes_registry.classify(data=None, filename=f)
            P.setMimeType(mi.normalized())
            P.setIconPath(mi.icon_path)
            l.append(P) 

        return l

registerType(PloneLocalFolderNG, PROJECTNAME)
