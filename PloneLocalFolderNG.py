import os
from urllib import quote

from DateTime.DateTime import DateTime
from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.FSObject import FSObject
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField, StringWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.CMFCore.CMFCorePermissions import *
from config import PROJECTNAME

schema = BaseSchema +  Schema((
    StringField('folder',
                widget=StringWidget(label='Local directory name')
                ),
    ))

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
        if os.path.isdir(self._filepath): return ''

        try: return os.stat(self._filepath)[6]
        except: return ''

InitializeClass(FileProxy)


class PloneLocalFolderNG(BaseContent):
    """ PloneLocalFolderNG """

    schema = schema
    security = ClassSecurityInfo()

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/plfng_view',
        'permissions': (View,)
        },)

    security.declareProtected('View', 'showFile')
    def showFile(self, destpath, REQUEST, RESPONSE):
        """ view file """

        mi = self.mimetypes_registry.classify(data=None, filename=destpath)
        RESPONSE.setHeader('content-type', mi.normalized())
        RESPONSE.setHeader('content-length', str(os.stat(destpath)[6]))
        if REQUEST.get('action', '') == 'download':
            REQUEST.RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' % os.path.basename(destpath))
        fp = open(destpath)
        while 1:
            data = fp.read(32768)
            if data:    
                RESPONSE.write(data)
            else:
                break
        fp.close()

    security.declareProtected('View', 'getContents')
    def getContents(self,  REQUEST=None):
        """ list content of local filesystem """

        show_dir = '/'.join(REQUEST['_e'])
        
        if show_dir.startswith('/') or show_dir.find('..') > -1:
            raise ValueError('illegal directory: %s' % show_dir)
        destfolder = os.path.normpath(os.path.join(self.folder, show_dir))
        if not destfolder.startswith(self.folder):
            raise ValueError('illegal directory: %s' % show_dir)

    
        rel_dir = destfolder.replace(self.folder, '')
        if rel_dir.startswith('/'): rel_dir = rel_dir[1:]

        l = []
        for f in os.listdir(destfolder):

            fullname = os.path.join(destfolder, f)
            P = FileProxy(f, fullname, f)
            mi = self.mimetypes_registry.classify(data=None, filename=f)

            if os.path.isdir(fullname):
                P.setIconPath('folder_icon.gif')
                P.setAbsoluteURL(self.absolute_url() + '/' +  os.path.join(rel_dir, f) + '/plfng_view')
                P.setMimeType('directory')
            else:
                P.setIconPath(mi.icon_path)
                P.setAbsoluteURL(self.absolute_url() + '/' +  os.path.join(rel_dir, f))
                P.setMimeType(mi.normalized())
            l.append(P) 

        return l

    security.declareProtected('View', 'breadcrumbs')
    def breadcrumbs(self, instance): 
        """ breadcrumbs """

        l = []
        sofar = []
        for d in instance.absolute_url(1).split('/'):
            sofar.append(d)
            l.append((d,'/'+'/'.join(sofar)))

        sofar = []
        for d in instance.REQUEST['_e']:
            sofar.append(d)
            l.append( (d, '%s/%s/plfng_view' % (instance.absolute_url(), '/'.join(sofar))) )
        return l

    def __call__(self, REQUEST, RESPONSE, *args, **kw):
        rel_dir = '/'.join(REQUEST.get('_e', []))
        destpath = os.path.join(self.folder, rel_dir)

        if os.path.isfile(destpath):
            return self.showFile(destpath, REQUEST, RESPONSE)
        else:
            RESPONSE.redirect('/' + os.path.join(self.absolute_url(1), rel_dir, 'plfng_view'))
            
    def __bobo_traverse__(self, REQUEST, name, RESPONSE=None):
        if not REQUEST.has_key('_e'): 
            REQUEST['_e'] = []

        destpath = os.path.join(self.folder, '/'.join(REQUEST['_e']), name)
        if os.path.exists(destpath): 
            REQUEST['_e'].append(name)
            return self
        else:
            try: return getattr(self, name)
            except AttributeError: pass
            REQUEST.RESPONSE.notFoundError(name)


def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('references',):
            a['visible'] = 0
    fti['filter_content_types'] = 1
    fti['allowed_content_types'] = ()
    return fti

registerType(PloneLocalFolderNG, PROJECTNAME)
