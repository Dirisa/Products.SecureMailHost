import os

from DateTime.DateTime import DateTime

from Products.CMFCore.FSObject import FSObject
from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

import zLOG

class FileProxy(FSObject):
    """A fake File proxy class """

    security = ClassSecurityInfo()
    meta_type = 'PloneLocalFolderFileProxy'

    def setMimeType(self, mt):
        self.mime_type = mt

    def setIconPath(self, icon_path):
        self.icon_path = icon_path

    def setAbsoluteURL(self, url):
        self.url = url

    def setComment(self, comment):
        self.comment = comment

    security.declarePublic('absolute_url')
    def absolute_url(self,relative=0):
        """ return url """
        return self.url

    security.declarePublic('title_or_id')
    def title_or_id(self):
        """ return title or id """
        return self.id

    security.declarePublic('getComment')
    def getComment(self):
        """ return comment"""
        return self.comment

    security.declarePublic('getTypeInfo')
    def getTypeInfo(self):
        """ return type info """
        TI = TypeInfo(self.id, self.mime_type)
        TI.setMimeType(self.mime_type)
        return TI

    def _readFile(self, *args, **kw):
        """ read the file """
    
    security.declarePublic('getIcon')
    def getIcon(self, arg=None):
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
        if os.path.isdir(self._filepath):
           return ''
        try:
           size = os.stat(self._filepath)[6]
           return size
        except: return ''
        
    def txng_get(self, attr):
        """ TextIndexNG support method that returns the source 
        (file body contents), mime type and encoding type of the file """

        if attr[0] in ('PrincipiaSearchSource', 'SearchableText'):
           fp = self.url
           file = open(fp, 'rb')
           try: source = file.read()
           finally: file.close()
           return source, self.mime_type, self.encoding
        
        elif attr[0] == 'id':
           source = self.id
           return source, self.mime_type, self.encoding
        
        else:
           return None
           
    def Description( self ):
        """ return an empty string as the description for the item """
        return ''             

InitializeClass(FileProxy)


class TypeInfo(SimpleItem):
    """ fake TypeInfo class to make CMF happy """

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