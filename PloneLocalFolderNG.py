import os
import shutil
from string import split,find

from DateTime.DateTime import DateTime
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission

from OFS.ObjectManager import checkValidId
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField, StringWidget
from Products.Archetypes.public import BooleanField, BooleanWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE,CEILING_DATE

from Products.CMFCore.CMFCorePermissions import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from config import *
from util import *
from FileProxy import FileProxy

import zLOG

from Acquisition import aq_chain

try:
    from Products.mxmCounter import mxmCounter
except ImportError:
    zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "Warning: mxmCounter was not imported")
    mxmCounter = None

schema = BaseSchema +  Schema((
    StringField('folder',
                validators=("isValidExistingFolderPath",),
                write_permission=CMFCorePermissions.ManagePortal,
                required=1,
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
                default=1,
                widget=BooleanWidget(
                        label='Generate MD5 after upload?',
                        description='Generate an MD5 checksum for a file immediately after it is uploaded.',
                        ),
                 ),
    StringField('external_syscall_md5',
                default='none',
                validators=("isValidExternalMD5Utility",),
                write_permission=CMFCorePermissions.ManagePortal,
                required=1,
                widget=StringWidget(label='external md5 system call',
                                    description='To use the standard python md5 implementation, specify "none".',
                       )
                ),
    StringField('quota_maxbytes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='0',
                widget=StringWidget(label='max # bytes quota limit',
                                    description='Prevent users from performing actions that would violate quota limits as follows: -1 -> use parent-level quota_maxbytes; 0 -> no limit, n -> # bytes quota limit',)
                ),
    BooleanField ('allow_file_unpacking',
                write_permission=CMFCorePermissions.ManagePortal,
                default=1,
                widget=BooleanWidget(
                        label='Allow File Unpacking?',
                        description='Allow users to extract the contents of archive files (eg, .zip, .tar) on to server local filesystem.',
                        ),
                ),
    StringField('hidden_file_prefixes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='.',
                widget=StringWidget(label='hide files with these prefixes',
                                    description='this field contains the comma-separated list of filename prefixes used to determine which files to hide',)
                ),
    StringField('hidden_file_suffixes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='.metadata,.plfngtmp',
                widget=StringWidget(label='hide files with these suffixes',
                                    description='this field contains the comma-separated list of filename suffixes used to determine which files to hide',)
                ),
    StringField('hidden_file_names',
                write_permission=CMFCorePermissions.ManagePortal,
                default='',
                widget=StringWidget(label='hide files with these exact names',
                                    description='this field contains the comma-separated list of filenames to hide',)
                ),            
    StringField('hidden_folder_prefixes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='.',
                widget=StringWidget(label='hide folders with these prefixes',
                                    description='this field contains the comma-separated list of folder prefixes used to determine which files to hide',)
                ),
    StringField('hidden_folder_suffixes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='.metadata,.plfngtmp',
                widget=StringWidget(label='hide folders with these suffixes',
                                    description='this field contains the comma-separated list of folder suffixes used to determine which files to hide',)
                ),
    StringField('hidden_folder_names',
                write_permission=CMFCorePermissions.ManagePortal,
                default='CVS',
                widget=StringWidget(label='hide folders with these exact names',
                                    description='this field contains the comma-separated list of folders to hide',)
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
    StringField('folder_address_display_style',
               default='currentIdOnly',
               required=1,
               vocabulary='getAddressDisplayStyleVocab',
               widget=SelectionWidget(
                  label='Folder Address Display Style',
                  description="""Select the folder address style to be displayed""",
                  format="select",),
      ),
    BooleanField ('fileBackup_enabled',
                write_permission=CMFCorePermissions.ManagePortal,
                default=0,
                widget=BooleanWidget(
                        label='Enable file backup on upload overwrite?',
                        description='Enable this field to archive files (to the backup-folder path) that will be overwritten by uploaded files.',
                        ),
                ),
    StringField('backup_folder',
                validators=("isValidExistingFolderPath",),
                write_permission=CMFCorePermissions.ManagePortal,
                required=0,
                widget=StringWidget(label='Local backup directory name')
                ),            
    ))


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
      { 'id': 'folderlisting',
        'name': 'Folder Listing',
        'action': 'string:${object_url}/plfng_view',
        'permissions': (View,),
        'visible'       : 0
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
      { 'id': 'diagnostics',
        'name': 'Diagnostics',
        'action': 'string:$object_url/plfng_summary',
        'permissions': (ManagePortal,),
        },          
      { 'id': 'metadata',
        'name': 'Properties',
        'action': 'string:${object_url}/base_metadata',
        'permissions': (ManageProperties,),  
        },
      )

    
    security.declareProtected(ManagePortal, 'getFileRealPath')
    def getFileRealPath(self, REQUEST):
        """ get the real (file system) path for the file """
        rel_dir = '/'.join(REQUEST.get('_e', []))
        return os.path.join(self.folder, rel_dir)
    
    security.declareProtected('View', 'getFileMetadata')
    def getFileMetadata(self, REQUEST, section="GENERAL", option="comment"):
        """ get file metadata"""
        rel_dir = '/'.join(REQUEST.get('_e', []))
        destpath = os.path.join(self.folder, rel_dir)
        #zLOG.LOG('PLFNG', zLOG.INFO , "getFileMetadata() :: destpath = %s" % destpath)
        metadataText = getMetadataElement(destpath, section, option)
        return metadataText
    
    security.declareProtected('View', 'getAvailableQuotaSpace')
    def getAvailableQuotaSpace(self):
        """ get the remaining space in # of bytes that are available for storage
            by the PLFNG instance without violating its byte quantity quota limit.
            A positive or zero return value indicates remaining space in # of bytes.
            A negative return value indicates that parent-level quota_maxbytes
            attribute is to be used to determine the remaining space in # of bytes """
        
        # if quota_maxbytes for PLFNG instance > 0  :: use its value

        # if quota_maxbytes for PLFNG instance = 0  :: return -1 (quota limit checking disabled)

        # if quota_maxbytes for PLFNG instance < 0 ::         
        #   traverse up the acquisition tree looking for first container with 
        #   a non-zero 'quota_maxbytes' attribute.  If such a container is found,
        #   find out the total number of bytes used by the contents of this container
            
        PLFNGInstanceQuotaLimit = int(self.quota_maxbytes)
        
        if PLFNGInstanceQuotaLimit > 0:
           quotaLimit = int(self.quota_maxbytes)
           folderProps = self.getProperties()
           usedBytes = folderProps['size']
           max_allowed_bytes = quotaLimit - usedBytes
           if max_allowed_bytes < 0: 
              max_allowed_bytes = 0
           
        elif PLFNGInstanceQuotaLimit == 0:
           max_allowed_bytes = -1

        else:
           quotaLimit = 0
           for parent in self.aq_chain[1:]:
              if hasattr(parent, "quota_maxbytes"):
                 quotaLimit = int(getattr(parent, "quota_maxbytes"))
                 if quotaLimit > 0:
                    usedBytes = determine_bytes_usage(parent)
                    break
           if quotaLimit > 0:
              max_allowed_bytes = quotaLimit - usedBytes
              if max_allowed_bytes < 0: 
                 max_allowed_bytes = 0      
           else:
              max_allowed_bytes = -1
              
        return max_allowed_bytes  
    
    security.declareProtected(ModifyPortalContent, 'setFileMetadata')
    def setFileMetadata(self, REQUEST, section, option, newvalue):
        """ set the metadata for the file """
        result = 0
        #zLOG.LOG('PLFNG', zLOG.INFO , "setFileMetadata() :: section=%s option=%s newvalue=%s" % (section, option, newvalue))
        rel_dir = '/'.join(REQUEST.get('_e', []))
        targetFile = os.path.join(self.folder, rel_dir)

        if section and option and newvalue:
            result = setMetadata(targetFile, section, option, newvalue)
        
        if result == 1:
            REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_editMetadata?portal_status_message=file metadata updated.')
        else:
            REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_editMetadata?portal_status_message=Error updating file metadata.')

    security.declareProtected(View, 'updateFileMetadatum')
    def updateFileMetadatum(self, REQUEST, section, option, mode='testonly'):
        """ update a metadatum for the file """
        result = 0
        #zLOG.LOG('PLFNG', zLOG.INFO , "setFileMetadata() :: section=%s option=%s newvalue=%s" % (section, option, newvalue))
        rel_dir = '/'.join(REQUEST.get('_e', []))
        targetFile = os.path.join(self.folder, rel_dir)
        
        if section == 'DIAGNOSTICS' and option == 'md5':
           metadataMD5 = getMetadataElement(targetFile, section, option)
           start_time = DateTime()
           fileMD5 = generate_md5(targetFile,self.external_syscall_md5)
           stop_time = DateTime()
           elapsed_time = (stop_time - start_time)*86400.0
           
           if metadataMD5 == fileMD5:
               if mode == 'testonly':
                   REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_editMetadata?portal_status_message=MD5 metadata is valid.  (MD5 computation took '+str(elapsed_time)[:6]+' seconds).') 
               else:
                   REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_editMetadata?portal_status_message=no need to update MD5 metadata (it is valid).')
           else:
               if mode == 'testonly':
                   REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_editMetadata?portal_status_message=WARNING: MD5 metadata does NOT match current file MD5 !!!') 
               else:
                   result = setMetadata(targetFile, section, option, fileMD5)
                   if result == 1:
                        REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_editMetadata?portal_status_message=MD5 metadata updated.')
                   else:
                        REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_editMetadata?portal_status_message=ERROR: MD5 metadata could not be updated !!!')

        else:
           REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_editMetadata?portal_status_message=Unsupported metadata update type.')
               
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

        # provide necessary default values if REQUEST is missing
        if REQUEST==None:
            show_dir = ''
        else:    
            show_dir = '/'.join(REQUEST['_e'])
            
        trimmedFolderBasePath = os.path.normpath(self.folder)

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

    security.declareProtected('View', 'listFolderContents')
    def listFolderContents(self,  spec=None, contentFilter=None, suppressHiddenFiles=0, REQUEST=None, RESPONSE=None):
        """ list content of local filesystem """
        
        filteredFileList = []
        filteredFolderList = []
        
        #zLOG.LOG('PLFNG', zLOG.INFO , "listFolderContents() :: REQUEST = %s" % REQUEST)
        #zLOG.LOG('PLFNG', zLOG.INFO , "listFolderContents() :: self.REQUEST = %s" % self.REQUEST)
                
        if REQUEST==None:
            self.REQUEST.RESPONSE.redirect( self.REQUEST['URL1'] + '/plfng_view' )
            #zLOG.LOG('PLFNG', zLOG.INFO , "listFolderContents() :: self.REQUEST[URL1] = %s" % self.REQUEST['URL1'])
            return []
            
            #zLOG.LOG('PLFNG', zLOG.INFO , "listFolderContents() :: self.REQUEST = %s" % self.REQUEST)
            #self.REQUEST.RESPONSE.redirect( self.absolute_url() + '/plfng_view' )
        else:    
            rel_dir = '/'.join(REQUEST.get('_e', []))
            show_dir = '/'.join(REQUEST['_e'])
            action = REQUEST.get('action', '')

        destpath = os.path.join(self.folder, rel_dir)
        
        if action == 'deleteFolder':
           #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "getContents() :: calling deleteFolder(%s)" % destpath)
           self.deleteFolder(rel_dir, destpath, REQUEST)
           return []
        
        else:
           this_portal = getToolByName(self, 'portal_url')
           mimetypesTool = getToolByName(this_portal, 'mimetypes_registry')
 
           if hasattr(self, "hidden_file_prefixes") and self.hidden_file_prefixes:
              filePrefixesSkipList = split(self.hidden_file_prefixes,',')
           else:
              filePrefixesSkipList = []
           
           if hasattr(self, "hidden_file_suffixes") and self.hidden_file_suffixes:
              fileSuffixesSkipList = split(self.hidden_file_suffixes,',')
           else:
              fileSuffixesSkipList = []
           
           if hasattr(self, "hidden_file_names") and self.hidden_file_names:
              fileNamesSkipList = split(self.hidden_file_names,',')
           else:
              fileNamesSkipList = []
           
           if hasattr(self, "hidden_folder_prefixes") and self.hidden_folder_prefixes:
              folderPrefixesSkipList = split(self.hidden_folder_prefixes,',')
           else:
              folderPrefixesSkipList = []
           
           if hasattr(self, "hidden_folder_suffixes") and self.hidden_folder_suffixes:
              folderSuffixesSkipList = split(self.hidden_folder_suffixes,',')
           else:
              folderSuffixesSkipList = []
           
           if hasattr(self, "hidden_folder_names") and self.hidden_folder_names:
              folderNamesSkipList = split(self.hidden_folder_names,',')
           else:
              folderNamesSkipList = []
              
           
           trimmedFolderBasePath = os.path.normpath(self.folder)
           
           if show_dir.startswith('/') or show_dir.find('..') > -1:
               raise ValueError('illegal directory: %s' % show_dir)
   
           destfolder = os.path.join(trimmedFolderBasePath, show_dir)
           
           if not destfolder.startswith(trimmedFolderBasePath):
               raise ValueError('illegal directory: %s' % show_dir)

           rel_dir = destfolder.replace(self.folder, '')
           if rel_dir.startswith('/'): rel_dir = rel_dir[1:]

           filteredFileList, filteredFolderList = \
              getFilteredFSItems(FSfullPath=destfolder, 
                                 skipInvalidIds=1, 
                                 mimetypesTool=mimetypesTool,  
                                 filetypePhrasesSkipList=[], 
                                 filePrefixesSkipList=filePrefixesSkipList, 
                                 fileSuffixesSkipList=fileSuffixesSkipList, 
                                 fileNamesSkipList=fileNamesSkipList,
                                 folderPrefixesSkipList=folderPrefixesSkipList, 
                                 folderSuffixesSkipList=folderSuffixesSkipList, 
                                 folderNamesSkipList=folderNamesSkipList)
           
           proxyObjectsList = []   
              
           for f in filteredFolderList:
                  
               FSfullPathFolderName = os.path.join(destfolder, f)
               P = FileProxy(id=f, filepath=FSfullPathFolderName, fullname=f, properties=None)
               mi = self.mimetypes_registry.classify(data=None, filename=f)
   
               P.setIconPath('folder_icon.gif')
               P.setAbsoluteURL(self.absolute_url() + '/' +  os.path.join(rel_dir, f) + '/plfng_view')
               P.setMimeType('folder')
               if os.path.exists(FSfullPathFolderName + '.metadata'):
                   try:
                     P.setComment(getMetadataElement(FSfullPathFolderName, section="GENERAL", option="comment"))
                   except:
                     P.setComment('')
               else:
                   P.setComment('')
               proxyObjectsList.append(P)
           
           for f in filteredFileList:
               
               FSfullPathFileName = os.path.join(destfolder, f)
               FSfullPathFolderName = os.path.dirname(FSfullPathFileName)
               P = FileProxy(id=f, filepath=FSfullPathFileName, fullname=FSfullPathFileName, properties=None)
               mi = self.mimetypes_registry.classify(data=None, filename=f)
           
               P.setIconPath(mi.icon_path)
               P.setAbsoluteURL(self.absolute_url() + '/' +  os.path.join(rel_dir, f))
               P.setMimeType(mi.normalized())
      
               if os.path.exists(FSfullPathFileName + '.metadata'):
                   try:
                     P.setComment(getMetadataElement(FSfullPathFileName, section="GENERAL", option="comment"))
                   except:
                     P.setComment('')
               else:
                   P.setComment('')
               proxyObjectsList.append(P)

           return proxyObjectsList

    security.declareProtected(CMFCorePermissions.AccessContentsInformation,
                              'folderlistingFolderContents')
    def folderlistingFolderContents(self, spec=None, contentFilter=None,
                                    suppressHiddenFiles=0 ):
        """
        Calls listFolderContents in protected only by ACI so that folder_listing
        can work without the List folder contents permission, as in CMFDefault
        """
        return self.listFolderContents(spec, contentFilter, suppressHiddenFiles)


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
        #zLOG.LOG('PLFNG', zLOG.INFO , "__call__() :: REQUEST = %s" % REQUEST)
        
        if REQUEST == None:
            return None

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
               #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "__call__() :: %s :: isfile()" % destpath)
               if REQUEST.get('action', '') == 'unpack':
                  self.unpackFile(os.path.dirname(rel_dir), destpath, REQUEST, RESPONSE)
               
               elif REQUEST.get('action', '') == 'deleteFile':
                  self.deleteFile(rel_dir, destpath, REQUEST, RESPONSE)
                  
               elif REQUEST.get('action', '') == 'catalog':
                  #catalogTool = getToolByName(self, 'portal_catalog')
                  return self.catalogContents()
               elif REQUEST.get('action', '') == 'editMetadata':
                  RESPONSE.redirect(('/' + os.path.join(self.absolute_url(1), rel_dir, 'plfng_editMetadata')).replace('\\','/'))   
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
            if REQUEST.has_key('RESPONSE'):
                REQUEST.RESPONSE.notFoundError(name)

    security.declareProtected(ModifyPortalContent, 'addFile')
    def addFile(self, sourceFSfullPath, destPLFNGrelativePath='', destBasename=None, moveFile=0, inputMD5=None):
        """ add a file """

        # 1st, make sure that the PLFNG instance is configured with valid FS folder
        
        if self.validFolder() != 1:
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: Error! PLFNG instance failed validFolder() test." )
           return 0
           
        # make sure that a file was specified

        if not os.path.isfile(sourceFSfullPath):
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: Error! sourceFSfullPath = %s not a file" % sourceFSfullPath )
           return 0
        
        if not destBasename:
           destBasename = os.path.basename(sourceFSfullPath)
        
        # make sure destination file name is valid   

        checkValidIdResult = checkValidId(destBasename)
        if checkValidIdResult != 1:
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: Error! destination filename (%s) is not permitted: %s" % (destBasename,checkValidIdResult))
           return 0
    
        # make sure the PLFNG destination relative path is valid   

        if destPLFNGrelativePath.startswith('/'):
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: Error! PLFNG destination path (%s) cannot begin with forward slash" % destPLFNGrelativePath)
           return 0
        
        pathItemList = split(destPLFNGrelativePath,'/')
        for pathItem in pathItemList:
           checkValidIdResult = checkValidId(destBasename)
           if checkValidIdResult != 1:
              zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: Error! PLFNG destination path (%s) invalid: %s" % (destPLFNGrelativePath,checkValidIdResult))
              return 0
           
        # make sure this add operation will not violate quota limit restrictions

        max_allowed_bytes = self.getAvailableQuotaSpace()
        contentLength = 0 # mpg fix this!!!  
        if max_allowed_bytes != -1 and contentLength > max_allowed_bytes:
           # uploaded file rejected as it would result in quota limit being exceeded
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: file rejected! CONTENT_LENGTH (%s) + usedBytes(%s) > max_allowed_bytes(%s)" % (contentLength,usedBytes, max_allowed_bytes) )
           return 0

        # if a MD5 checksum was provided, make sure that the server-generated MD5 matches it
        
        serverMD5 = None
        if inputMD5:
           serverMD5 = generate_md5(sourceFSfullPath,self.external_syscall_md5)
           if inputMD5 != serverMD5:
              zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: file rejected! inputMD5 (%s) != generated MD5 (%s)" % (inputMD5,serverMD5) )
              return 0

        # create destination path as necessary
        
        destFSfullPathFolderName = os.path.join(self.folder, destPLFNGrelativePath)
        
        if not os.path.exists(destFSfullPathFolderName):
           try:
              os.makedirs(destFSfullPathFolderName)
           except:
              zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: Error! could not create FS destination path folders (%s)" % destFSfullPathFolderName )
              return 0
        
        # backup existing file as necessary
        
        destFSfullPath = os.path.join(destFSfullPathFolderName, destBasename)
        
        if not os.path.exists(destFSfullPath):    
           newRevisionNumber = 1 
        
        else:    
           # get revision of existing file (or 1 if revision metadata missing)
           oldRevisionNumberText = getMetadataElement(destFSfullPath, section="GENERAL", option="revision")
           if oldRevisionNumberText:
              oldRevisionNumber = int(oldRevisionNumberText)
           else:
              oldRevisionNumber = 1
                
           newRevisionNumber = oldRevisionNumber + 1
            
           # backup existing file if file backup is enabled & backup_folder path is set  
           if self.fileBackup_enabled and self.backup_folder:
              backupdestpath = os.path.join(self.backup_folder, destPLFNGrelativePath)

              if not oldRevisionNumberText:
                 setMetadata(destFSfullPath, section="GENERAL", option="revision", value=oldRevisionNumber)
                
              # move existing file to backup location renamed with trailing rev.#
              backupFileSuffix = '.' + str(oldRevisionNumber)
              backupfilename = os.path.join(backupdestpath, destBasename) + backupFileSuffix
              # create skeleton directory structure under backupFolder if necessary 
              if not os.path.exists(backupdestpath): os.makedirs(backupdestpath)
              shutil.move(destFSfullPath, backupfilename)
        
        # copy/move file to destination path

        try:
           if moveFile==1:
              shutil.move(sourceFSfullPath, destFSfullPath)
           else:
              shutil.copy(sourceFSfullPath, destFSfullPath)
        except:
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: Error! could not add file" )
           return 0
        
        return newRevisionNumber   

    security.declareProtected(ModifyPortalContent, 'HTMLFormUploadFile')
    def HTMLFormUploadFile(self, upload, comment, REQUEST, clientMD5=None):
        """ upload a file via HTML form-based file upload mechanism """

        rel_dir = '/'.join(REQUEST.get('_e', []))
        destpath = os.path.join(self.folder, rel_dir)
        uploadFileBaseName = os.path.basename(upload.filename)
        if self.backup_folder:
            backupdestpath = os.path.join(self.backup_folder, rel_dir)
        else:
            backupdestpath = None

        if not upload:
            REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=no file was uploaded!')
            return 0        
        
        if self.require_MD5_with_upload and not clientMD5:
            REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=you MUST provide the MD5 checksum for the file you want to upload!')
            return 0

        filename = os.path.join(destpath, os.path.basename(upload.filename))
        tmpfile = filename + '.plfngtmp'
        f = open(tmpfile, 'wb')
        f.write(upload.read())
        f.close()
        serverMD5 = None
        
        newRevisionNumber = \
         self.addFile(sourceFSfullPath=tmpfile,
                     destPLFNGrelativePath=rel_dir,
                     destBasename=os.path.basename(filename),
                     moveFile=1,
                     inputMD5=clientMD5)
        
        if newRevisionNumber == 0:
           os.remove(tmpfile)
           REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file rejected.')
        else:
           
           # ------------------------- apply metadata ---------------------------------
           # GENERAL:
           #   comments - comments on the file
           #   source   - userId of the source/uploader/provider
           #   revision - the PLFNG centric revision # of this file
           # DIAGNOSTICS:
           #   md5      - md5 checksum generated by the server for the file
           # ARCHIVEINFO:
           #   numUnpackedFiles   - # files that the packed file contains
           #   sizezUnpackedFiles - total # bytes for all of the unpacked files 
           # CHANGELOG:
           #   history  - (tbd)
           # -------------------------------------------------------------------------
           
           # GENERAL: 'comments' option
           if comment:
               setMetadata(filename, section="GENERAL", option="comment", value=comment)
   
           # GENERAL: 'source' option
           portal = getToolByName(self, 'portal_url').getPortalObject()
           portal_membership = getToolByName(portal, 'portal_membership')
           if portal_membership.isAnonymousUser():
               creator = 'anonymous'
           else:
               creator = portal_membership.getAuthenticatedMember().getId()
           setMetadata(filename, section="GENERAL", option="source", value=creator)
           
           # GENERAL: 'revision' option
           setMetadata(filename, section="GENERAL", option="revision", value=newRevisionNumber)
           
           # DIAGNOSTICS: 'md5' option
           if clientMD5:
               setMetadata(filename, section="DIAGNOSTICS", option="md5", value=clientMD5)
           
           # if .zip file, set ARCHIVEINFO metadata
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
    def unpackFile(self, plfngRelativeDir, FSpackedFile, REQUEST, RESPONSE):
        """ unpack a file """

        # for now, unzip is the only type of unpacking implemented
        
        # 1st, make sure the file is an unpackable type
        if not self.mimetypes_registry.classify(data=None, filename=FSpackedFile) == 'application/zip':
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
               unpackedSize = int(getMetadataElement(FSpackedFile, section="ARCHIVEINFO", option="unpacked_size"))
            except:
               try:
                  setZipInfoMetadata(FSpackedFile)
                  unpackedSize = int(getMetadataElement(FSpackedFile, section="ARCHIVEINFO", option="unpacked_size"))
               except:
                  RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file could not be unpacked (not a valid file?!).')
                  return 0
            if max_allowed_bytes > 0 and (unpackedSize + usedBytes) > max_allowed_bytes:
               REQUEST.RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file cannot be unpacked as doing so would violate quota limit.')
               zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "unpackFile() :: unpack rejected! unpackedSize (%s) + usedBytes(%s) > max_allowed_bytes(%s)" % (unpackedSize,usedBytes, max_allowed_bytes) )
               return 0
        # if we made it to this point, unpack the file
        if self.backup_folder:
            backupdestpath = os.path.join(self.backup_folder, plfngRelativeDir)
        else:
            backupdestpath = None
        
        if upzipFile(FSfilename=FSpackedFile, FSBackupFolderBase=backupdestpath):
            RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file unpacked.')
            return 1
        else:
            RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=file could not be unpacked.')
            return 0



    
    security.declareProtected('Delete objects', 'deleteFile')
    def deleteFile(self, rel_dir, fileToDelete, REQUEST, RESPONSE):
        """ delete the file """
        
        if not os.path.exists(fileToDelete):
           return 0
        else:   
           # move file to backupFolder if file backup is enabled & backup_folder path is set  
           if self.fileBackup_enabled and self.backup_folder:
               # get revision of existing file (or 1 if revision metadata missing)
               oldRevisionNumberText = getMetadataElement(fileToDelete, section="GENERAL", option="revision")
               if oldRevisionNumberText:
                   oldRevisionNumber = int(oldRevisionNumberText)
               else:
                   oldRevisionNumber = 1
                   # uncomment the following line to update the file's metadata if its also going to be backed up 
                   #setMetadata(fileToDelete, section="GENERAL", option="revision", value=oldRevisionNumber)
                   
               # move existing file to backup location renamed with trailing rev.#
               backupdestpath = os.path.dirname(os.path.join(self.backup_folder,rel_dir))
               backupFileSuffix = '.' + str(oldRevisionNumber)
               backupfilename = os.path.join(backupdestpath, os.path.basename(fileToDelete)) + backupFileSuffix
               # create skeleton directory structure under backupFolder if necessary 
               if not os.path.exists(backupdestpath): os.makedirs(backupdestpath)
               shutil.move(fileToDelete, backupfilename)
           else:
               os.remove(fileToDelete)
           
           metadataFileToDelete = fileToDelete + '.metadata'
           if os.path.exists(metadataFileToDelete):
               os.remove(metadataFileToDelete)

           RESPONSE.redirect(REQUEST['URL1']+'/plfng_view?portal_status_message=' + rel_dir + ' deleted.')
           return 1

    security.declareProtected('Delete objects', 'deleteFolder')
    def deleteFolder(self, rel_dir, folderToDelete, REQUEST):
        """ delete the folder """
        shutil.rmtree(folderToDelete)
        REQUEST.RESPONSE.redirect(REQUEST['URL2']+'/plfng_view?portal_status_message=' + rel_dir + ' deleted.')
        return 1

    def catalogContents(self,rel_dir=None, catalog='portal_catalog'):
        filesCataloged = 0
        filesNotCataloged = 0
        filetypePhrasesSkipList = []
        meta_type = "FileProxy"
        # set View permission for all cataloged files to that of the PLFNG object
        perm = Permission(View,'',self) 
        view_roles = perm.getRoles()
        effective = FLOOR_DATE
        expires = CEILING_DATE  
        
        this_portal = getToolByName(self, 'portal_url')
        catalogTool = getToolByName(this_portal, catalog)
        mimetypesTool = getToolByName(this_portal, 'mimetypes_registry')
        portalId = this_portal.getPortalObject().getId()
        
        if self.filetypes_not_to_catalog:
           filetypePhrasesSkipList = split(self.filetypes_not_to_catalog,',')

        if rel_dir == None: rel_dir = ''
        FSfullPathFolderName = os.path.join(self.folder, rel_dir)
        
        uidBase = str('/' + portalId + '/'+ this_portal.getRelativeContentURL(self) + '/')

        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: FSfullPathFolderName=%s " % FSfullPathFolderName )
        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: rel_dir=%s" % rel_dir )
        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: portal path=%s" % this_portal.getRelativeContentURL(self) )
        
        filesCataloged = \
           catalogFSContent(FSfullPath=FSfullPathFolderName, 
                            filetypePhrasesSkipList=filetypePhrasesSkipList,
                            catalogTool=catalogTool,
                            mimetypesTool=mimetypesTool,
                            uidBase=uidBase,
                            view_roles=view_roles,
                            effective=effective,
                            expires=expires,
                            meta_type=meta_type)

        return filesCataloged

    security.declarePublic('allowedContentTypes')
    def allowedContentTypes( self ):
        """
            List type info objects for types which can be added in
            this folder.
        """
        return []
        
    security.declareProtected(CMFCorePermissions.View,'getAddressDisplayStyleVocab')
    def getAddressDisplayStyleVocab(self):
        return DisplayList(
           (
            ('PLFNG_Base_Relative','PLFNG_Base_Relative'),
           ))
        
    security.declareProtected('View', 'getFilteredOutContents')
    def getFilteredOutContents(self,rel_dir=None):
        """ list filtered out content of local filesystem """
        
        illegalFilesList = []
        filteredOutFileList = []
        filteredOutFolderList = []
        
        filteredFileList = []
        filteredFolderList = []

        if rel_dir == None: rel_dir = ''
        destpath = os.path.join(self.folder, rel_dir)
        
        this_portal = getToolByName(self, 'portal_url')
        mimetypesTool = getToolByName(this_portal, 'mimetypes_registry')

        if hasattr(self, "hidden_file_prefixes") and self.hidden_file_prefixes:
           filePrefixesSkipList = split(self.hidden_file_prefixes,',')
        else:
           filePrefixesSkipList = []
        
        if hasattr(self, "hidden_file_suffixes") and self.hidden_file_suffixes:
           fileSuffixesSkipList = split(self.hidden_file_suffixes,',')
        else:
           fileSuffixesSkipList = []
        
        if hasattr(self, "hidden_file_names") and self.hidden_file_names:
           fileNamesSkipList = split(self.hidden_file_names,',')
        else:
           fileNamesSkipList = []
        
        if hasattr(self, "hidden_folder_prefixes") and self.hidden_folder_prefixes:
           folderPrefixesSkipList = split(self.hidden_folder_prefixes,',')
        else:
           folderPrefixesSkipList = []
        
        if hasattr(self, "hidden_folder_suffixes") and self.hidden_folder_suffixes:
           folderSuffixesSkipList = split(self.hidden_folder_suffixes,',')
        else:
           folderSuffixesSkipList = []
        
        if hasattr(self, "hidden_folder_names") and self.hidden_folder_names:
           folderNamesSkipList = split(self.hidden_folder_names,',')
        else:
           folderNamesSkipList = []
           
        
        trimmedFolderBasePath = os.path.normpath(destpath)
        
        illegalFilesList, illegalFoldersList, filteredOutFileList, filteredOutFolderList = \
           getFilteredOutFSItems(FSfullPath=trimmedFolderBasePath,
                              PLFNGrelPath=rel_dir, 
                              skipInvalidIds=1, 
                              mimetypesTool=mimetypesTool,  
                              filetypePhrasesSkipList=[], 
                              filePrefixesSkipList=filePrefixesSkipList, 
                              fileSuffixesSkipList=fileSuffixesSkipList, 
                              fileNamesSkipList=fileNamesSkipList,
                              folderPrefixesSkipList=folderPrefixesSkipList, 
                              folderSuffixesSkipList=folderSuffixesSkipList, 
                              folderNamesSkipList=folderNamesSkipList)

        filteredFileList, filteredFolderList = \
           getFilteredFSItems(FSfullPath=trimmedFolderBasePath, 
                                 skipInvalidIds=1, 
                                 mimetypesTool=mimetypesTool,  
                                 filetypePhrasesSkipList=[], 
                                 filePrefixesSkipList=filePrefixesSkipList, 
                                 fileSuffixesSkipList=fileSuffixesSkipList, 
                                 fileNamesSkipList=fileNamesSkipList,
                                 folderPrefixesSkipList=folderPrefixesSkipList, 
                                 folderSuffixesSkipList=folderSuffixesSkipList, 
                                 folderNamesSkipList=folderNamesSkipList)
        
        for subFolder in filteredFolderList:
           new_rel_dir = os.path.join(rel_dir,subFolder)
           sub_illegalFilesList, sub_illegalFoldersList, sub_filteredOutFileList, sub_filteredOutFolderList = \
              self.getFilteredOutContents(rel_dir = new_rel_dir)
              
           illegalFilesList = illegalFilesList + sub_illegalFilesList
           illegalFoldersList = illegalFoldersList + sub_illegalFoldersList
           filteredOutFileList = filteredOutFileList + sub_filteredOutFileList
           filteredOutFolderList = filteredOutFolderList + sub_filteredOutFolderList
        
        return illegalFilesList, illegalFoldersList, filteredOutFileList, filteredOutFolderList 
   
           
def _getFolderProperties(FSfullPathFolderName):
   
   filteredFileList = []
   filteredFolderList = []
   bytesInFolder = 0
   folderCount = 0
   fileCount = 0
   
   filteredFileList, filteredFolderList = \
      getFilteredFSItems(FSfullPath=FSfullPathFolderName,
                         skipInvalidIds=1, 
                         mimetypesTool=None,
                         filetypePhrasesSkipList=[], 
                         filePrefixesSkipList=[], 
                         fileSuffixesSkipList=['.metadata','.plfngtmp'], 
                         fileNamesSkipList=[],
                         folderPrefixesSkipList=[], 
                         folderSuffixesSkipList=[], 
                         folderNamesSkipList=[])
   
   fileCount = fileCount + len(filteredFileList)
   folderCount = folderCount + len(filteredFolderList)
   
   for f in filteredFileList:
      FSfullPathFileName = os.path.join(FSfullPathFolderName,f)
      try: file_size = os.stat(FSfullPathFileName)[6]
      except: file_size = 0
      bytesInFolder = bytesInFolder + file_size
   
   for subfolder in filteredFolderList:
      subfolderFullName = os.path.join(FSfullPathFolderName, subfolder)
      subfolder_props = _getFolderProperties(subfolderFullName)
      bytesInFolder = bytesInFolder + subfolder_props.get('size',0)
      folderCount = folderCount + subfolder_props.get('folders',0)
      fileCount = fileCount + subfolder_props.get('files',0)
     
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



