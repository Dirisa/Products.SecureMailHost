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

    def setAbsoluteURL(self, url):
        self.url = url

    security.declarePublic('absolute_url')
    def absolute_url(self):
        """ return url """
        return self.url

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
        try:
            return DateTime(os.stat(self._filepath)[8])
        except:
            return DateTime()

    security.declarePublic('get_size')
    def get_size(self):
        """ None """
        try:
            return os.stat(self._filepath)[6]
        except:
            return ''

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


    def viewfile(self, REQUEST):
        """ view file """

        fullname = os.path.join(self.folder, REQUEST['viewfile'])
        mi = self.mimetypes_registry.classify(data=None, filename=fullname)
        REQUEST.RESPONSE.setHeader('content-type', mi.normalized())
        REQUEST.RESPONSE.setHeader('content-length', str(os.stat(fullname)[6]))
#        REQUEST.RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' % os.path.basename(REQUEST['viewfile']))
        fp = open(fullname)
                
        while 1:
            data = fp.read(32768)
            if data:    
                REQUEST.RESPONSE.write(data)
            else:
                break
        fp.close()

    def getContents(self,  REQUEST=None):
        """ list content of local filesystem """

        if REQUEST.has_key('viewfile'):
            return self.viewfile(REQUEST)
    
        if REQUEST.has_key('showdir'):
            show_dir = REQUEST['showdir']
            if show_dir.startswith('/') or show_dir.find('..') > -1:
                raise ValueError('illegal directory: %s' % show_dir)
            destfolder = os.path.normpath(os.path.join(self.folder, show_dir))
            if not destfolder.startswith(self.folder):
                raise ValueError('illegal directory: %s' % show_dir)
        else:
            destfolder = self.folder

        rel_dir = destfolder.replace(self.folder, '')
        if rel_dir.startswith('/'): rel_dir = rel_dir[1:]

        l = []
        for f in os.listdir(destfolder):

            fullname = os.path.join(destfolder, f)
            P = FileProxy(f, fullname, f)
            mi = self.mimetypes_registry.classify(data=None, filename=f)
            P.setMimeType(mi.normalized())

            if os.path.isdir(fullname):
                P.setIconPath('folder_icon.gif')
                P.setAbsoluteURL(self.absolute_url() + '?showdir=' + os.path.join(rel_dir, f))
            else:
                P.setIconPath(mi.icon_path)
                P.setAbsoluteURL(self.absolute_url() + '?viewfile=' + os.path.join(rel_dir, f))
            l.append(P) 

        return l

registerType(PloneLocalFolderNG, PROJECTNAME)
