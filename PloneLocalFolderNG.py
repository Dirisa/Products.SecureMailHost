import os
from urllib import quote
from string import split,find

from DateTime.DateTime import DateTime
from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.FSObject import FSObject
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField, StringWidget
from Products.Archetypes.public import BooleanField, BooleanWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE,CEILING_DATE
from Products.CMFCore.CMFCorePermissions import *
from Products.CMFCore import CMFCorePermissions
from config import *
from util import *
import zLOG
from Products.CMFCore.utils import getToolByName

from Acquisition import aq_chain

from App.FindHomes import INSTANCE_HOME   # eg, windows INSTANCE_HOME = C:\Plone\Data

try:
    from Products.mxmCounter import mxmCounter
except ImportError:
    zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "ImportError :: mxmCounter")
    mxmCounter = None

schema = BaseSchema +  Schema((
    StringField('folder',
                validators=("isValidExistingFolderPath",),
                write_permission=CMFCorePermissions.ManagePortal,
                required=1,
                default=INSTANCE_HOME,
                widget=StringWidget(label='Local directory name')
                ),
    BooleanField ('require_MD5_with_upload',
                write_permission=CMFCorePermissions.ManagePortal,
                default=0,
                widget=BooleanWidget(
                        label='Require MD5 with file upload?',
                        description='Require user to provide MD5 checksum along with file being uploaded.',
                        ),
                ),
    BooleanField ('generate_MD5_after_upload',
                write_permission=CMFCorePermissions.ManagePortal,
                default=0,
                widget=BooleanWidget(
                        label='Generate MD5 after upload?',
                        description='Generate an MD5 checksum for a file immediately after it is uploaded.',
                        ),
                 ),
    BooleanField ('quota_aware',
                write_permission=CMFCorePermissions.ManagePortal,
                default=0,
                widget=BooleanWidget(
                        label='Quota Aware?',
                        description='Prevent users from performing actions that would violate parent-level folder quota limits.',
                        ),
                ),
    BooleanField ('allow_file_unpacking',
                write_permission=CMFCorePermissions.ManagePortal,
                default=0,
                widget=BooleanWidget(
                        label='Allow File Unpacking?',
                        description='Allow users to extract the contents of archive files (eg, .zip, .tar) on to server local filesystem.',
                        ),
                ),
    BooleanField ('cataloging_enabled',
                write_permission=CMFCorePermissions.ManagePortal,
                default=1,
                widget=BooleanWidget(
                        label='Is file cataloging enabled?',
                        description='This field controls whether or not files can be cataloged.',
                        ),
                ),                
    StringField('filetypes_not_to_catalog',
                write_permission=CMFCorePermissions.ManagePortal,
                default='image/,video/,audio/',
                widget=StringWidget(label='filetypes for catalog action to skip',
                                    description='this comma-separated list of (partial) mimetype phrases is used by the catalog action to determine which files NOT to catalog',)
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
        if os.path.isdir(self._filepath): return ''

        try: return os.stat(self._filepath)[6]
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


class PloneLocalFolderNG(BaseContent):
    """ PloneLocalFolderNG """

    isPrincipiaFolderish=1
    content_icon = 'folder_icon.gif'
    schema = schema
    security = ClassSecurityInfo()

    actions = (
      { 'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/plfng_view',
        'permissions': (View,),
        },
      { 'id': 'edit',
        'name': 'Edit',
        'action': 'string:$object_url/base_edit',
        'permissions': (ManagePortal,),
        },
      { 'id': 'catalog',
        'name': 'Catalog',
        'action': 'string:$object_url/plfng_catalog',
        'permissions': (ManagePortal,),
        },        
        
      { 'id': 'metadata',
        'name': 'Properties',
        'action': 'string:${object_url}/base_metadata',
        'permissions': (ManageProperties,),  
        },
      )

    security.declareProtected('View', 'showFile')
    def showFile(self, destpath, REQUEST, RESPONSE):
        """ view file """

        mi = self.mimetypes_registry.classify(data=None, filename=destpath)
        RESPONSE.setHeader('content-type', mi.normalized())
        RESPONSE.setHeader('content-length', str(os.stat(destpath)[6]))
        if REQUEST.get('action', '') == 'download':
            REQUEST.RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' % os.path.basename(destpath))
        fp = open(destpath, 'rb')
        while 1:
            data = fp.read(32768)
            if data:    
                RESPONSE.write(data)
            else:
                break
        fp.close()
        
        # mxmCounter (v1.1.0, http://www.mxm.dk/products/public/mxmCounter)
        # is a nice little hit counter, but to get it to count hits on PLFNG
        # files, I opted to call it here since PLFNG files don't show with the
        # standard footer.pt where I place the mxmCounter::count() routine.
        #
        #   Note: for the following code to work with mxmCounter (v1.1.0), you 
        #         will need to modify/extend the mxmCounter class by adding the 
        #         following method:
        #
        #         def proxyObject_increase_count(self,url_path): 
        #            return increase_count(url_path, self.save_interval)
        #
        #   I have contacted the mxmCounter author to ask that this type of
        #   functionality be added to the baseline of mxmCounter.
        
        if mxmCounter:
            url_path = REQUEST['URLPATH0']
            #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "showFile() :: mxmCounter file=%s" % url_path )
            this_portal = getToolByName(self, 'portal_url') 
            try:
               mxmCounter_obj = getattr( this_portal,'mxm_counter' )
               mxmCounter_obj.proxyObject_increase_count(url_path)
            except:
               zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "showFile() :: there was a problem with mxmCounter" )
         
    security.declareProtected('View', 'validFolder')
    def validFolder(self,  REQUEST=None):
        """ determine if the requested folder path is legal and exists """

        trimmedFolderBasePath = os.path.normpath(self.folder)
        show_dir = '/'.join(REQUEST['_e'])
        #zLOG.LOG('PLFNG', zLOG.INFO , "validFolder() :: show_dir = %s" % show_dir)
        #zLOG.LOG('PLFNG', zLOG.INFO , "validFolder() :: trimmedFolderBasePath = %s" % trimmedFolderBasePath)
        
        if show_dir.startswith('/') or show_dir.find('..') > -1:
            raise ValueError('illegal directory: %s' % show_dir)
        
        destfolder = os.path.normpath(os.path.join(trimmedFolderBasePath, show_dir))
        
        if not destfolder.startswith(trimmedFolderBasePath):
            zLOG.LOG('PLFNG', zLOG.INFO , "validFolder() :: destfolder = %s" % destfolder)
            zLOG.LOG('PLFNG', zLOG.INFO , "validFolder() :: trimmedFolderBasePath = %s" % trimmedFolderBasePath)
            raise ValueError('illegal directory: %s' % show_dir)

        if os.path.exists(destfolder):
            #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "validFolder() :: path ok for: %s" %destfolder )
            return 1
        else:
            zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "validFolder() :: !!! path bad for: %s" %destfolder )
            return 0

        
    security.declareProtected('View', 'getContents')
    def getContents(self,  REQUEST=None):
        """ list content of local filesystem """
        
        this_portal = getToolByName(self, 'portal_url')
        mimetypesTool = getToolByName(this_portal, 'mimetypes_registry')

        trimmedFolderBasePath = os.path.normpath(self.folder)
        show_dir = '/'.join(REQUEST['_e'])
        
        if show_dir.startswith('/') or show_dir.find('..') > -1:
            raise ValueError('illegal directory: %s' % show_dir)

        destfolder = os.path.join(trimmedFolderBasePath, show_dir)
        
        if not destfolder.startswith(trimmedFolderBasePath):
            raise ValueError('illegal directory: %s' % show_dir)

    
        rel_dir = destfolder.replace(self.folder, '')
        if rel_dir.startswith('/'): rel_dir = rel_dir[1:]

        l = []
        if os.path.exists(destfolder):
           for f in os.listdir(destfolder):
               if f.endswith('.metadata'): continue
   
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
   
               if os.path.exists(fullname + '.metadata'):
                   try:
                     P.setComment(getMetadataElement(fullname, section="GENERAL", option="comment"))
                   except:
                     P.setComment('')
               else:
                   P.setComment('')
               l.append(P) 

        else:
            zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "getContents() :: destfolder not found (%s)" % destfolder )
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

    def __call__(self, REQUEST=None, RESPONSE=None, *args, **kw):
        if not hasattr(self, "folder"):
            #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "__call__() :: no folder attribute")
            return self
        #elif not REQUEST:
        #    zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "__call__() :: no REQUEST")
        #    raise NotImplementedError, "PLFNG objects can only be created and viewed through the Plone interface."
        else:     
           rel_dir = '/'.join(REQUEST.get('_e', []))
           destpath = os.path.join(self.folder, rel_dir)
   
           if os.path.isfile(destpath):
               
               if REQUEST.get('action', '') == 'unpack':
                  self.unpackFile(destpath, REQUEST, RESPONSE)
               
               elif REQUEST.get('action', '') == 'delete':
                  self.deleteFile(rel_dir, destpath, REQUEST, RESPONSE)   
               
               elif REQUEST.get('action', '') == 'catalog':
                  #catalogTool = getToolByName(self, 'portal_catalog')
                  return self.catalogContents()
               else: 
                  return self.showFile(destpath, REQUEST, RESPONSE)
           else:
   
               #  Mozilla browsers don't like backslashes in URLs, so replace any '\' with '/'
               #  that os.path.join might produce
               RESPONSE.redirect(('/' + os.path.join(self.absolute_url(1), rel_dir, 'plfng_view')).replace('\\','/'))
          
            
    def __bobo_traverse__(self, REQUEST, name, RESPONSE=None):
        #zLOG.LOG('PLFNG', zLOG.INFO , "__bobo_traverse__() :: type(self.REQUEST) = %s" % type(self.REQUEST))
        #zLOG.LOG('PLFNG', zLOG.INFO , "__bobo_traverse__() :: REQUEST = %s" % REQUEST)
        #zLOG.LOG('PLFNG', zLOG.INFO , "__bobo_traverse__() :: name = %s" % name)
        
        if not REQUEST.has_key('_e'): 
            REQUEST['_e'] = []
            
        if not hasattr(self, "folder"):
            zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "__bobo_traverse__() :: no folder attribute")
            raise NotImplementedError, "This PLFNG object has not been properly configured (folder attribute missing). Add it through the regular Plone interface?!"

        destpath = os.path.join(self.folder, '/'.join(REQUEST['_e']), name)
        if os.path.exists(destpath): 
            REQUEST['_e'].append(name)
            return self
        else:
            try: return getattr(self, name)
            except AttributeError: pass
            REQUEST.RESPONSE.notFoundError(name)

    security.declareProtected(ModifyPortalContent, 'upload_file')
    def upload_file(self, upload, comment, REQUEST, clientMD5=None):
        """ upload a file """

        rel_dir = '/'.join(REQUEST.get('_e', []))
        destpath = os.path.join(self.folder, rel_dir)
        
        if not upload:
            REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=no file was uploaded!')
            return 0        
        
        if self.require_MD5_with_upload and not clientMD5:
            REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=you MUST provide the MD5 checksum for the file you want to upload!')
            return 0
        
        if self.quota_aware:
            # traverse up the acquisition tree looking for first container with 
            # a non-zero 'quota_maxbytes' attribute.  If such a container is found,
            # find out the total number of bytes used by the contents of this
            # container in order to determine if the addition of the newly uploaded 
            # file will exceed quota_maxbytes --in which case reject it.  
            
            max_allowed_bytes = 0

            for parent in self.aq_chain[1:]:
               if hasattr(parent, "quota_maxbytes"):
                  max_allowed_bytes = int(getattr(parent, "quota_maxbytes"))
                  if max_allowed_bytes > 0:
                     usedBytes = determine_bytes_usage(parent)
                     break
            
            contentLength = int(REQUEST.get_header('CONTENT_LENGTH'))
            
            #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upload_file() :: CONTENT_LENGTH=%d usedBytes=%d max_allowed_bytes=%d" % (contentLength,usedBytes, max_allowed_bytes) )


            if max_allowed_bytes > 0 and (contentLength + usedBytes) > max_allowed_bytes:
                 REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=uploaded file rejected as it would result in quota limit being exceeded.')
                 zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upload_file() :: file rejected! CONTENT_LENGTH (%s) + usedBytes(%s) > max_allowed_bytes(%s)" % (contentLength,usedBytes, max_allowed_bytes) )
                 return 0
        
        filename = os.path.join(destpath, os.path.basename(upload.filename))
        open(filename, 'wb').write(upload.read())
        
        serverMD5 = None
        
        #set DIAGNOSTICS (md5) metadata
        if self.generate_MD5_after_upload:
            serverMD5 = generate_md5(filename)
            setMetadata(filename, section="DIAGNOSTICS", option="md5", value=serverMD5)
        
        # reject if client-provided MD5 for uploaded file does not match server-generated MD5
        if self.require_MD5_with_upload:
            if not serverMD5:
               serverMD5 = generate_md5(filename)
               setMetadata(filename, section="DIAGNOSTICS", option="md5", value=serverMD5)
            if clientMD5 != serverMD5:
               os.remove(filename)
               os.remove(filename+'.metadata')
               zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upload_file()::MD5 CHECK FAILED...DELETED: %s + associated .metadata file" % filename )
               REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=uploaded file failed MD5 integrity test and was deleted!')
               return 0
        
        #set SOURCE metadata
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_membership = getToolByName(portal, 'portal_membership')
        if portal_membership.isAnonymousUser():
            creator = 'anonymous'
        else:
            creator = portal_membership.getAuthenticatedMember().getId()
        setMetadata(filename, section="GENERAL", option="source", value=creator)
        
        # set COMMENT metadata
        if comment:
            #open(filename + '.metadata', 'wb').write(comment)
            setMetadata(filename, section="GENERAL", option="comment", value=comment)
        
        # if .zip file, set ZIPINFO metadata
        if self.mimetypes_registry.classify(data=None, filename=upload.filename) == 'application/zip':
            setZipInfoMetadata(filename)

        REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file added.')

    security.declareProtected(ModifyPortalContent, 'create_directory')
    def create_directory(self, dirname, REQUEST):
        """ create a sub-directory """
        dirname = dirname.replace('\\','/')
        if dirname.startswith('/') or dirname.find('..') > -1 or dirname.find(':') > -1:
            zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "create_directory()::ABORTED...illegal directory name: %s " % dirname )
            REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=ERROR! illegal directory name (new directory name must be relative path)')
            return 0

        rel_dir = '/'.join(REQUEST.get('_e', []))
        destpath = os.path.join(self.folder, rel_dir, dirname)
        print destpath
        if os.path.exists(destpath):
            raise ValueError('Directory %s already exists' % dirname)

        try:
            os.makedirs(destpath)    # try..except to avoid exposing the realword path
        except:
            raise RuntimeError('Directory could not be created')
        
        url = '/' + os.path.join(self.absolute_url(1), rel_dir, dirname) + '/plfng_view?portal_status_message=Directory created'
        REQUEST.RESPONSE.redirect(url)

    security.declareProtected('View', 'getProperties')
    def getProperties(self, REQUEST=None):
        """ get the summary properties for the local filesystem directory for this class instance """

        trimmedFolderBasePath = os.path.normpath(self.folder)
        show_dir = '/'.join(REQUEST['_e'])
        
        if show_dir.startswith('/') or show_dir.find('..') > -1:
            raise ValueError('illegal directory: %s' % show_dir)

        destfolder = os.path.normpath(os.path.join(self.folder, show_dir))
        
        if not destfolder.startswith(trimmedFolderBasePath):
            raise ValueError('illegal directory: %s' % show_dir)

        localfolder_props = _getFolderProperties(destfolder)
                
        return localfolder_props

    security.declareProtected('View', 'get_size')
    def get_size(self):
        """ return the size of the underlying contents """
        
        localfolder_props = _getFolderProperties(self.folder)
        
        return localfolder_props.get('size',0)

    security.declareProtected(ModifyPortalContent, 'unpackFile')
    def unpackFile(self, packedFile, REQUEST, RESPONSE):
        """ unpack a file """

        # for now, unzip is the only type of unpacking implemented
        
        # 1st, make sure the file is an unpackable type
        if not self.mimetypes_registry.classify(data=None, filename=packedFile) == 'application/zip':
            RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file cannot be unpacked (not a recognized packed file type).')
            return 0
        # then, make sure the file unpacking property is set
        elif not self.allow_file_unpacking:
            RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file unpacking is not allowed here.')
            return 0
        # then, make sure that unpacking the file will not violate applicable quota-limits
        elif self.quota_aware:
            # traverse up the acquisition tree looking for first container with 
            # a non-zero 'quota_maxbytes' attribute.  If such a container is found,
            # find out the total number of bytes used by the contents of this
            # container in order to determine if the addition of the unpacked 
            # contents of the file will exceed quota_maxbytes --in which case 
            # do not carry out the unpack operation.  
            
            max_allowed_bytes = 0

            for parent in self.aq_chain[1:]:
               if hasattr(parent, "quota_maxbytes"):
                  max_allowed_bytes = int(getattr(parent, "quota_maxbytes"))
                  if max_allowed_bytes > 0:
                     usedBytes = determine_bytes_usage(parent)
                     break
            
            try:
               unpackedSize = int(getMetadataElement(packedFile, section="ZIPINFO", option="unpacked_size"))
            except:
               try:
                  setZipInfoMetadata(packedFile)
                  unpackedSize = int(getMetadataElement(packedFile, section="ZIPINFO", option="unpacked_size"))
               except:
                  RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file could not be unpacked (not a valid file?!).')
                  return 0
            if max_allowed_bytes > 0 and (unpackedSize + usedBytes) > max_allowed_bytes:
               REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file cannot be unpacked as doing so would violate quota limit.')
               zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "unpackFile() :: unpack rejected! unpackedSize (%s) + usedBytes(%s) > max_allowed_bytes(%s)" % (unpackedSize,usedBytes, max_allowed_bytes) )
               return 0
        # if we made it to this point, unpack the file
        if upzipFile(packedFile):
            RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file unpacked.')
            return 1
        else:
            RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file could not be unpacked.')
            return 0

    security.declareProtected('Delete objects', 'deleteFile')
    def deleteFile(self, rel_dir, fileToDelete, REQUEST, RESPONSE):
        """ delete the file """
        os.remove(fileToDelete)
        RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=' + rel_dir + ' deleted.')
        return 1

    security.declareProtected('View', 'quota_aware')
    def quota_aware(self): 
        """ return quota_aware value """
        return self.quota_aware

    security.declareProtected('View', 'requireUploadMD5')
    def requireUploadMD5(self): 
        """ return require_MD5_with_upload value """
        return self.require_MD5_with_upload

    security.declareProtected('View', 'genMD5OnUpload')
    def genMD5OnUpload(self): 
        """ return generate_MD5_after_upload value """
        return self.generate_MD5_after_upload

    security.declareProtected('View', 'fileUnpackingAllowed')
    def fileUnpackingAllowed(self): 
        """ return allow_file_unpacking value """
        return self.allow_file_unpacking 

    security.declareProtected('View', 'catalogingEnabled')
    def catalogingEnabled(self): 
        """ return cataloging_enabled value """
        return self.cataloging_enabled 
        
    def catalogContents(self,rel_dir=None, catalog='portal_catalog'):
        
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portalId = portal.getId()
        
        if self.filetypes_not_to_catalog:
         filetypePhrasesSkipList = split(self.filetypes_not_to_catalog,',')
        else:
         filetypePhrasesSkipList = []
        
        filesCataloged = 0
        filesNotCataloged = 0
        
        if rel_dir == None: rel_dir = ''
        fullfoldername = os.path.join(self.folder, rel_dir)
        
        dummyFileProxy = FileProxy("dummy", fullfoldername, "dummy")
        dummyFileProxy.meta_type = "FileProxy"
        # set View permission for all files to that of the PLFNG object
        perm = Permission(View,'',self)
        view_roles = perm.getRoles()
        dummyFileProxy._View_Permission = view_roles
        # set 'effective' and 'expires' keys
        dummyFileProxy.effective = FLOOR_DATE
        dummyFileProxy.expires = CEILING_DATE  

        this_portal = getToolByName(self, 'portal_url')
        catalogTool = getToolByName(this_portal, catalog)
        mimetypesTool = getToolByName(this_portal, 'mimetypes_registry')

        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: fullfoldername=%s " % fullfoldername )
        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: rel_dir=%s" % rel_dir )
        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: portal path=%s" % this_portal.getRelativeContentURL(self) )
        
        for f in os.listdir(fullfoldername):
            # don't include the PloneLocalFolderNG special metadata files  
            if f.endswith('.metadata'): continue
      
            itemFullName = os.path.join(fullfoldername, f)

            if os.path.isdir(itemFullName): 
                new_rel_dir = os.path.join(rel_dir,f)
                #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: subdir=%s" % new_rel_dir )
                subfolderfilesCataloged,subfolderfilesNotCataloged = self.catalogContents(new_rel_dir)
                filesCataloged = filesCataloged + subfolderfilesCataloged
                filesNotCataloged = filesNotCataloged + subfolderfilesNotCataloged
                
            else:
                uid = str('/' + portalId + '/'+ this_portal.getRelativeContentURL(self) + '/' +  os.path.join(rel_dir, f).replace('\\','/'))
                
                dummyFileProxy.id = str(f)
                dummyFileProxy.url = itemFullName
                dummyFileProxy.encoding = None
                mi = mimetypesTool.classify(data=None, filename=f)
                dummyFileProxy.setIconPath(mi.icon_path)
                dummyFileProxy.mime_type = mi.normalized()
                
                # check to see if the mimetype for this file is on the skip list. 
                # The main reason for this is to avoid having TextIndexNG2 process 
                # files that we know it doesnt handle, but this could also be useful
                # for other scenarios.
                 
                skipFile = 0
                for filetypePhrase in filetypePhrasesSkipList:
                  if dummyFileProxy.mime_type.find(filetypePhrase) >= 0: skipFile=1
                
                if skipFile:
                  filesNotCataloged = filesNotCataloged + 1
                  #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: not cataloging file=%s" % dummyFileProxy.url )
                else:
                  #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: file=%s" % itemFullName )
                  #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: mimetype=%s" % dummyFileProxy.mime_type )
                  #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: catalog uid=%s" % uid )
                      
                  catalogTool.catalog_object( dummyFileProxy, uid )
                      
                  filesCataloged = filesCataloged + 1
        return filesCataloged, filesNotCataloged            


def _getFolderProperties(fullfoldername):
   bytesInFolder = 0
   folderCount = 0
   fileCount = 0
   if os.path.exists(fullfoldername):
      
      for f in os.listdir(fullfoldername):
         # don't include the PloneLocalFolderNG special metadata files  
         if f.endswith('.metadata'): continue
         
         itemFullName = os.path.join(fullfoldername, f)
   
         if os.path.isdir(itemFullName): 
            folderCount = folderCount + 1
            subfolder_props = _getFolderProperties(itemFullName)
            bytesInFolder = bytesInFolder + subfolder_props.get('size',0)
            folderCount = folderCount + subfolder_props.get('folders',0)
            fileCount = fileCount + subfolder_props.get('files',0)
         else:
            fileCount = fileCount + 1     
            try: file_size = os.stat(itemFullName)[6]
            except: file_size = 0
            bytesInFolder = bytesInFolder + file_size
           
   folderProps = { }
   folderProps['size'] = bytesInFolder
   folderProps['files'] = fileCount
   folderProps['folders'] = folderCount
   return folderProps 



def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('references',):
            a['visible'] = 0
    fti['filter_content_types'] = 1
    fti['allowed_content_types'] = ()
    return fti

registerType(PloneLocalFolderNG, PROJECTNAME)



