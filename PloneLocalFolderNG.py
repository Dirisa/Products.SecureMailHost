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

try:
    from ZPublisher.Iterators import filestream_iterator
    STREAM_SUPPORT=1
except ImportError:
    STREAM_SUPPORT=0

from config import *
from util import *
from FileProxy import FileProxy

import zLOG

from Acquisition import aq_chain

try:
    from Products.mxmCounter import mxmCounter
except ImportError:
    msg = "Warning: mxmCounter was not imported"
    zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)
    mxmCounter = None

schema = BaseSchema +  Schema((
    StringField('folder',
                validators=("isValidExistingFolderPath",),
                write_permission=CMFCorePermissions.ManagePortal,
                required=1,
                widget=StringWidget(label='Local directory name')
                ),
    StringField('default_page',
                write_permission=CMFCorePermissions.ManagePortal,
                default='',
                widget=StringWidget(label='filename of default page to view',
                                    description='specify the filename of the \
                                    default page to show (if file exists in \
                                    current folder) instead of current folder \
                                    contents for folder View action.  Leave \
                                    this empty to disable this default page \
                                    feature.',)
                ),
    BooleanField ('require_MD5_with_upload',
                write_permission=CMFCorePermissions.ManagePortal,
                default=0,
                widget=BooleanWidget(
                        label='Require MD5 with file upload?',
                        description='Require user to provide MD5 checksum \
                        along with file being uploaded.',
                        ),
                ),
    BooleanField ('generate_MD5_after_upload',
                write_permission=CMFCorePermissions.ManagePortal,
                default=1,
                widget=BooleanWidget(
                        label='Generate MD5 after upload?',
                        description='Generate an MD5 checksum for a file \
                        immediately after it is uploaded.',
                        ),
                 ),
    StringField('external_syscall_md5',
                default='none',
                validators=("isValidExternalMD5Utility",),
                write_permission=CMFCorePermissions.ManagePortal,
                required=1,
                widget=StringWidget(label='external md5 system call',
                                    description='To use the standard python \
                                    md5 implementation, specify "none".',
                       )
                ),
    StringField('quota_maxbytes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='0',
                widget=StringWidget(label='max # bytes quota limit',
                                    description='Prevent users from \
                                    performing actions that would violate \
                                    quota limits as follows: -1 -> use \
                                    parent-level quota_maxbytes; 0 -> no \
                                    limit, n -> # bytes quota limit',)
                ),
    BooleanField ('allow_file_unpacking',
                write_permission=CMFCorePermissions.ManagePortal,
                default=1,
                widget=BooleanWidget(
                        label='Allow File Unpacking?',
                        description='Allow users to extract the contents of \
                        archive files (eg, .zip, .tar) on to server local \
                        filesystem.',
                        ),
                ),
    StringField('hidden_file_prefixes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='.',
                widget=StringWidget(label='hide files with these prefixes',
                                    description='this field contains the \
                                    comma-separated list of filename prefixes \
                                    used to determine which files to hide',)
                ),
    StringField('hidden_file_suffixes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='.metadata,.plfngtmp',
                widget=StringWidget(label='hide files with these suffixes',
                                    description='this field contains the \
                                    comma-separated list of filename suffixes \
                                    used to determine which files to hide',)
                ),
    StringField('hidden_file_names',
                write_permission=CMFCorePermissions.ManagePortal,
                default='',
                widget=StringWidget(label='hide files with these exact names',
                                    description='this field contains the comma\
                                    -separated list of filenames to hide',)
                ),
    StringField('hidden_folder_prefixes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='.',
                widget=StringWidget(label='hide folders with these prefixes',
                                    description='this field contains the \
                                    comma-separated list of folder prefixes \
                                    used to determine which files to hide',)
                ),
    StringField('hidden_folder_suffixes',
                write_permission=CMFCorePermissions.ManagePortal,
                default='.metadata,.plfngtmp',
                widget=StringWidget(label='hide folders with these suffixes',
                                    description='this field contains the \
                                    comma-separated list of folder suffixes \
                                    used to determine which files to hide',)
                ),
    StringField('hidden_folder_names',
                write_permission=CMFCorePermissions.ManagePortal,
                default='CVS',
                widget=StringWidget(label='hide folders with these exact names',
                                    description='this field contains the \
                                    comma-separated list of folders to hide',)
                ),
    BooleanField ('cataloging_enabled',
                write_permission=CMFCorePermissions.ManagePortal,
                default=1,
                widget=BooleanWidget(
                        label='Is file cataloging enabled?',
                        description='This field controls whether or not files \
                        can be cataloged.',
                        ),
                ),
    StringField('filetypes_not_to_catalog',
                write_permission=CMFCorePermissions.ManagePortal,
                default='image/,video/,audio/',
                widget=StringWidget(label='filetypes for catalog action to skip',
                                    description='this comma-separated list of \
                                    (partial) mimetype phrases is used by the \
                                    catalog action to determine which files \
                                    NOT to catalog',)
                ),
    StringField('folder_address_display_style',
               default='currentIdOnly',
               required=1,
               vocabulary='getAddressDisplayStyleVocab',
               widget=SelectionWidget(
                  label='Folder Address Display Style',
                  description="""Select the folder address style to be \
                  displayed""",
                  format="select",),
      ),
    BooleanField ('fileBackup_enabled',
                write_permission=CMFCorePermissions.ManagePortal,
                default=0,
                widget=BooleanWidget(
                        label='Enable file backup on upload overwrite?',
                        description='Enable this field to archive files \
                        (to the backup-folder path) that will be overwritten \
                        by uploaded files.',
                        ),
                ),
    StringField('backup_folder',
                validators=("isValidExistingFolderPath",),
                write_permission=CMFCorePermissions.ManagePortal,
                required=0,
                widget=StringWidget(label='Local backup directory name')
                ),
    ))


def make_url(content, *args):
    import posixpath
    dest = ('/' + posixpath.join(content.absolute_url(1), *args))
    # Mozilla browsers don't like backslashes in URLs, so
    # replace any '\' with '/' that os.path.join might
    # produce
    return dest.replace('\\', '/')

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

    security.declareProtected(View, 'view')
    def view(self, REQUEST, RESPONSE):
        """Invokes the default view."""
        return self.__call__(REQUEST, RESPONSE)

    security.declareProtected(ManagePortal, 'getFileRealPath')
    def getFileRealPath(self):
        """ get the real (file system) path for the file """
        return self._getFSFullPath(PLFNGRelativePath='')

    security.declareProtected('View', 'getFileMetadata')
    def getFileMetadata(self, section="GENERAL", option="comment", rel_dir=''):
        """ get file metadata"""
        destpath = self._getFSFullPath(PLFNGRelativePath=rel_dir)
        #zLOG.LOG('PLFNG', zLOG.INFO , "getFileMetadata() :: \
        #destpath = %s" % destpath)
        metadataText = getMetadataElement(destpath, section, option)
        return metadataText

    security.declareProtected('View', 'getAvailableQuotaSpace')
    def getAvailableQuotaSpace(self):
        """ get the remaining space in # of bytes that are available for
            storage by the PLFNG instance without violating its byte quantity
            quota limit. A positive or zero return value indicates remaining
            space in # of bytes. A negative return value indicates that
            parent-level quota_maxbytes attribute is to be used to determine
            the remaining space in # of bytes """

        # if quota_maxbytes for PLFNG instance > 0  :: use its value

        # if quota_maxbytes for PLFNG instance = 0  :: return -1
        #   (quota limit checking disabled)

        # if quota_maxbytes for PLFNG instance < 0 ::
        #   traverse up the acquisition tree looking for first container with
        #   a non-zero 'quota_maxbytes' attribute.  If such a container is
        # found, find out the total number of bytes used by the contents of
        # this container

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
    def setFileMetadata(self, section, option, newvalue):
        """ set the metadata for the file """
        result = 0
        #zLOG.LOG('PLFNG', zLOG.INFO , "setFileMetadata() :: \
        #section=%s option=%s newvalue=%s" % (section, option, newvalue))

        targetFile = self._getFSFullPath(PLFNGRelativePath='')

        if section and option and newvalue:
            if len(section)==len(option)==len(newvalue):
                tmpres = len(section) > 0  # initialize to True
                for i in range(0,len(section)):
                    tmpres = tmpres and setMetadata(targetFile,
                                                    section[i],
                                                    option[i],
                                                    newvalue[i])
                # return True when all matadatas are successfully set
                result = tmpres

        if result == 1:
            self.REQUEST.RESPONSE.redirect(self.REQUEST['URL1']+\
            '/plfng_editMetadata?portal_status_message=file metadata updated.')
        else:
            msg = 'Error updating file metadata.'
            self.REQUEST.RESPONSE.redirect(REQUEST['URL1']+\
            '/plfng_editMetadata?portal_status_message=' + msg)

    security.declareProtected(ModifyPortalContent, 'updateMD5Metadatum')
    def updateMD5Metadatum(self,PLFNGrelativePath='',mode='',output='redir'):
        """ update (or test) the MD5 metadatum for the file """
        # INPUT:
        #   PLFNGrelativePath-
        #     if PLFNGrelativePath is provided, it will be used by 
        #     _getFSFullPath() to determine which target file this method will
        #     operate on. Otherwise, _getFSFullPath() will use the '_e' field 
        #     of self.REQUEST  to determine the target file.
        #   mode-
        #     'testonly' -> the MD5 metadatum for the file will only be tested
        #     'MD5only' -> only the current MD5 for the file will be generated
        #     'update' ->  the MD5 metadatum for the file will be updated
        #   output-
        #     'redir' -> the textual result of this method is provided through
        #                portal_status_message via plfng_editMetadata redirect
        #     otherwise, this method will return an integer result value
        #
        # OUTPUT:
        #  --------------------------------------------------------------------
        #     existing 
        #  metadata valid?	  mode?    output?         output behavior
        #  --------------------------------------------------------------------
        #        yes       'testonly' 'redir'  redirect: 'MD5 valid'
        #        no        'testonly' 'redir'  redirect: 'MD5 invalid warning'
        #        yes       'testonly'   ''                 -1
        #        no        'testonly'   ''                  0
        #        yes        'update'    ''                 -1
        #        no         'update'    ''                  1 *
        #        yes        'update'  'redir'  redirect: 'MD5 valid, no update'
        #        no         'update'  'redir'  redirect: 'MD5 metadata updated'
        #        yes       'MD5only'  'redir'  redirect: 'file MD5 is <md5>'
        #        no        'MD5only'  'redir'  redirect: 'file MD5 is <md5>'
        #        yes       'MD5only'    ''               <md5>
        #        no        'MD5only'    ''               <md5>
        #  --------------------------------------------------------------------
        #
        #    * return value will be 1 only if setMetadata() succeeds; otherwise 
        #      the return value will be 0

        result = 0
        section = 'DIAGNOSTICS'
        option = 'md5'

        targetFile = self._getFSFullPath(PLFNGRelativePath=PLFNGrelativePath)
        
        #msg = "updateMD5Metadatum() :: rel_dir=%s mode=%s output=%s target=%s"\
        #       % (PLFNGrelativePath, mode, output, targetFile)
        #zLOG.LOG('PLFNG', zLOG.INFO , msg)

        if not os.path.isfile(targetFile):
            #raise ValueError('not a file: %s' % PLFNGrelativePath)
            return None

        metadataMD5 = getMetadataElement(targetFile, section, option)
        start_time = DateTime()
        fileMD5 = generate_md5(targetFile,self.external_syscall_md5)
        stop_time = DateTime()
        elapsed_time = (stop_time - start_time)*86400.0

        if metadataMD5 == fileMD5:
            result = -1
            if mode == '' or mode=='testonly':
                msg = 'MD5 metadata is valid. (MD5 computation took '+ \
                      str(elapsed_time)[:6] + ' seconds).'
            elif mode == 'MD5only':
                result = fileMD5
                msg='current file MD5 is: ' + fileMD5
            elif mode =='update':
                msg = 'no need to update MD5 metadata (it is valid).'
        else:
            if mode == '' or mode == 'testonly':
                result = 0
                msg='WARNING: MD5 metadata does NOT match current file MD5 !!!'
            elif mode == 'MD5only':
                result = fileMD5
                msg='current file MD5 is: ' + fileMD5
            elif mode =='update':
                result = setMetadata(targetFile, section, option, fileMD5)
                if result == 1:
                     msg = 'MD5 metadata updated.'
                else:
                     msg = 'ERROR: MD5 metadata could not be updated !!!'

        if output == 'redir':
           self.REQUEST.RESPONSE.redirect(self.REQUEST['URL1']+\
           '/plfng_editMetadata?portal_status_message=' + msg)
        else:
           return result

    def _increment_mxmcount(self):
        """ backwards compatibility """
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
        REQUEST = self.REQUEST
        url_path = REQUEST['URLPATH0']
        this_portal = getToolByName(self, 'portal_url')
        try:
           mxmCounter_obj = getattr(this_portal, 'mxm_counter')
           mxmCounter_obj.proxyObject_increase_count(url_path)
        except:
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "showFile() :: \
           there was a problem with mxmCounter" )

    security.declareProtected('View', 'showFile')
    def showFile(self, destpath, REQUEST, RESPONSE):
        """ view file """

        mi = self.mimetypes_registry.classify(data=None,
                                              filename=destpath.lower())
        RESPONSE.setHeader('content-type', mi.normalized())
        RESPONSE.setHeader('content-length', str(os.stat(destpath)[6]))
        if REQUEST.get('action', '') == 'download':
            REQUEST.RESPONSE.setHeader('content-disposition',
                                       'attachment; filename=%s'
                                        % os.path.basename(destpath))

        fiter = None
        if STREAM_SUPPORT:
            fiter = filestream_iterator(destpath, 'rb')
        else:
            fp = open(destpath, 'rb')
            while 1:
                data = fp.read(32768)
                if data:
                    RESPONSE.write(data)
                else:
                    break
            fp.close()

        if mxmCounter:
            self._increment_mxmcount()

        return fiter

    security.declareProtected('View', 'validFolder')
    def validFolder(self):
        """ determine if the requested folder path is legal and exists """

        # Note: we do NOT want _getFSFullPath() to perform a redirect action
        # if the PLFNG instance folder path is invalid.  For now, this is not
        # a problem as the redirection logic in _getFSFullPath() doesnt appear
        # to work, but if it does start working, we will need to pass a control
        # param into it to tell it whether or not to redirect on error.

        try:
           rtn = self._getFSFullPath(PLFNGRelativePath='')
           return 1
        except:
           return 0

    def _getFSBasePath(self):
        """ returns the base File System path of the item. """

        if self.folder == '':
           request = self.REQUEST
           msg = 'local directory field of PLFNG instance not set!'
           redirURL = self.absolute_url() + '/base_edit?portal_status_message='+msg
           zLOG.LOG('PLFNG', zLOG.INFO , "_getFSBasePath(): redir = "+ redirURL)
           zLOG.LOG('PLFNG', zLOG.INFO , "_getFSBasePath(): request = %s" % request)
           request.RESPONSE.redirect( redirURL )
           # MG: not sure why, but the preceding redirect only works from ZMI,
           # so throw the following exception in case the redirect fails
           msg=msg + ' (use base_edit to fix)'
           raise ValueError(msg)

        trimmedFSBasePath = os.path.normpath(self.folder)

        if os.path.exists(trimmedFSBasePath):
            #msg = '_getFSBasePath() :: FSpath = ' + FSFullPath
            #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)
            return trimmedFSBasePath
        else:
            raise ValueError('non-existent path: %s' % trimmedFSBasePath)


    def _getFSFullPath(self, PLFNGRelativePath=''):
        """ returns the full File System path of the item.  Note: this
            is the PLFNG security gatekeeper method for all accesses
            to the local directory field of PLFNG instances. """

        trimmedFSBasePath = self._getFSBasePath()

        if not PLFNGRelativePath:
            PLFNGRelativePath = '/'.join(self.REQUEST.get('_e', []))

        # protect against potential '_e' shenanigans
        if PLFNGRelativePath.startswith('/') or \
          PLFNGRelativePath.find('..') > -1:
            msg = "illegal relative path: " + PLFNGRelativePath
            zLOG.LOG('PLFNG', zLOG.INFO , "validFolder() :: " + msg)
            raise ValueError(msg)

        #zLOG.LOG('PLFNG', zLOG.INFO , "validFolder() :: \
        #trimmedFSBasePath = %s" % trimmedFSBasePath)

        FSFullPath = \
         os.path.normpath(os.path.join(trimmedFSBasePath,PLFNGRelativePath))

        if not FSFullPath.startswith(trimmedFSBasePath):
            zLOG.LOG('PLFNG', zLOG.INFO , "_getFSFullPath() :: \
             FSFullPath = %s, trimmedFSBasePath = %s" % \
             (FSFullPath,trimmedFSBasePath))
            raise ValueError('illegal path: %s' % FSFullPath)

        if os.path.exists(FSFullPath):
            #msg = '_getFSFullPath() :: FSpath = ' + FSFullPath
            #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)
            return FSFullPath
        else:
            msg = "_getFSFullPath() :: path bad for: "+ FSFullPath
            zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)
            raise ValueError('illegal path: %s' % FSFullPath)

    def _createProxy(self, id, **kw):
        """ handle the details, nassty """
        from os.path import join, dirname, exists
        destination = kw['destination']
        proxy_type = kw.get('type', 'content')
        properties = kw.get('properties', None)
        rel_dir = kw['rel_dir']

        fullpath = join(destination, id)
        foldername = dirname(fullpath)
        mi = self.mimetypes_registry.classify(data=None, filename=id.lower())

        proxy = FileProxy(id, filepath=fullpath, fullname=fullpath,
                          properties=properties)
        proxy.setAbsoluteURL('%s/%s' % (self.absolute_url(), join(rel_dir,id)))

        if proxy_type == 'folder':
            proxy.setIconPath('folder_icon.gif')
            proxy.setMimeType('folder')
        else:
            proxy.setIconPath(mi.icon_path)
            proxy.setMimeType(mi.normalized())

        GENERAL_MD = getMetadataElements(fullpath, 'GENERAL') or {}
        proxy.setComment(GENERAL_MD.get('comment',''))
        proxy.setLanguage(GENERAL_MD.get('language','natural'))
        proxy.setRevision(GENERAL_MD.get('revision',''))
        proxy.setTitle(GENERAL_MD.get('title',''))

        DIAGNOSTICS_MD = getMetadataElements(fullpath, 'DIAGNOSTICS') or {}
        proxy.setChecksum(GENERAL_MD.get('md5',''))

        return proxy.__of__(self)

    def _getAttribute(self, attrname):
        """ method will return a list """
        attr = getattr(self, attrname, None)
        if attr is not None:
            return attr.split(',')
        return []

    security.declareProtected('View', 'contentValues')
    def contentValues(self, spec=None, filter=None, sort_on=None, reverse=0):
        """ CMFPlone.PloneFolder.PloneFolder.contentValues """
        filteredFileList = []
        filteredFolderList = []
        REQUEST = self.REQUEST

        portal = getToolByName(self, 'portal_url')
        mime_registry = getToolByName(portal, 'mimetypes_registry')

        destpath = self._getFSFullPath(PLFNGRelativePath='')

        trimmedFSBasePath = self._getFSBasePath()
        rel_dir = destpath.replace(trimmedFSBasePath, '')

        if rel_dir.startswith('/'): rel_dir = rel_dir[1:]

        #XXX smacks of some sort of data object
        filePrefixesSkip = self._getAttribute('hidden_file_prefixes')
        fileSuffixesSkip = self._getAttribute('hidden_file_suffixes')
        fileNamesSkip = self._getAttribute('hidden_file_names')
        folderPrefixesSkip = self._getAttribute('hidden_folder_prefixes')
        folderSuffixesSkip = self._getAttribute('hidden_folder_suffixes')
        folderNamesSkip = self._getAttribute('hidden_folder_names')

        #XXX smacking lips
        filteredFileList, filteredFolderList = getFilteredFSItems(
                             FSfullPath=destpath,
                             skipInvalidIds=1,
                             mimetypesTool=mime_registry,
                             filetypePhrasesSkipList=[],
                             filePrefixesSkipList=filePrefixesSkip,
                             fileSuffixesSkipList=fileSuffixesSkip,
                             fileNamesSkipList=fileNamesSkip,
                             folderPrefixesSkipList=folderPrefixesSkip,
                             folderSuffixesSkipList=folderSuffixesSkip,
                             folderNamesSkipList=folderNamesSkip)

        proxies = []
        for file in filteredFileList:
            _proxy = self._createProxy(file,
                                       rel_dir=rel_dir,
                                       destination=destpath)
            proxies.append(_proxy)

        for folder in filteredFolderList:
            _proxy = self._createProxy(folder,
                                       rel_dir=rel_dir,
                                       destination=destpath)
            proxies.append(_proxy)

        return proxies


    security.declareProtected('View', 'listFolderContents')
    def listFolderContents(self,  spec=None, contentFilter=None,
                           suppressHiddenFiles=0, REQUEST=None, RESPONSE=None):
        """ list content of local filesystem """

        filteredFileList = []
        filteredFolderList = []

        destpath = self._getFSFullPath(PLFNGRelativePath='')

        if REQUEST.get('action', '') == 'deleteFolder':
           self.deleteFolder(rel_dir, destpath, REQUEST)
           return []

        else:

           trimmedFSBasePath = self._getFSBasePath()

           relURL = destpath.replace(trimmedFSBasePath, '').replace('\\','/')

           #if relURL.startswith('/'): relURL = relURL[1:]
           relURL = relURL+'/'
           this_portal = getToolByName(self, 'portal_url')
           mimetypesTool = getToolByName(this_portal, 'mimetypes_registry')

           filePrefixesSkip = self._getAttribute('hidden_file_prefixes')
           fileSuffixesSkip = self._getAttribute('hidden_file_suffixes')
           fileNamesSkip = self._getAttribute('hidden_file_names')
           folderPrefixesSkip = self._getAttribute('hidden_folder_prefixes')
           folderSuffixesSkip = self._getAttribute('hidden_folder_suffixes')
           folderNamesSkip = self._getAttribute('hidden_folder_names')


           #msg = 'listFolderContents() :: calling getFilteredFSItems() :\
           # FSfullPath = ' + destpath
           #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)

           filteredFileList, filteredFolderList = \
              getFilteredFSItems(FSfullPath=destpath,
                                 skipInvalidIds=1,
                                 mimetypesTool=mimetypesTool,
                                 filetypePhrasesSkipList=[],
                                 filePrefixesSkipList=filePrefixesSkip,
                                 fileSuffixesSkipList=fileSuffixesSkip,
                                 fileNamesSkipList=fileNamesSkip,
                                 folderPrefixesSkipList=folderPrefixesSkip,
                                 folderSuffixesSkipList=folderSuffixesSkip,
                                 folderNamesSkipList=folderNamesSkip)

           proxyObjectsList = []

           for f in filteredFolderList:

               FSfullPathFolderName = os.path.join(destpath, f)
               P = FileProxy(id=f,
                             filepath=FSfullPathFolderName,
                             fullname=f,
                             properties=None)

               P.setIconPath('folder_icon.gif')
               P.setAbsoluteURL(self.absolute_url() + relURL + f)
               P.setMimeType('folder')
               if os.path.exists(FSfullPathFolderName + '.metadata'):
                   try:
                     P.setComment(getMetadataElement(FSfullPathFolderName,
                                                     section="GENERAL",
                                                     option="comment"))
                   except:
                     P.setComment('')
                   try:
                     P.setTitle(getMetadataElement(FSfullPathFolderName,
                                                   section="GENERAL",
                                                   option="title"))
                   except:
                     P.setTitle('')

               else:
                   P.setComment('')
                   P.setTitle('')

               proxyObjectsList.append(P)

           for file in filteredFileList:

               destpath = self._getFSFullPath(PLFNGRelativePath='')
               trimmedFSBasePath = self._getFSBasePath()
               rel_dir = destpath.replace(trimmedFSBasePath, '')
               if rel_dir.startswith('/'): rel_dir = rel_dir[1:]

               _proxy = self._createProxy(file,
                                          rel_dir=rel_dir,
                                          destination=destpath)

               proxyObjectsList.append(_proxy)

           return proxyObjectsList

    security.declareProtected(CMFCorePermissions.AccessContentsInformation,
                              'folderlistingFolderContents')
    def folderlistingFolderContents(self, spec=None, contentFilter=None,
                                    suppressHiddenFiles=0 ):
        """
        Calls listFolderContents in protected only by ACI so that
        folder_listing can work without the List folder contents permission,
        as in CMFDefault
        """
        return self.listFolderContents(spec,contentFilter,suppressHiddenFiles)


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
            l.append( (d, '%s/%s/plfng_view' % \
                      (instance.absolute_url(), '/'.join(sofar))) )
        return l

    def __call__(self, REQUEST=None, RESPONSE=None, *args, **kw):
        #zLOG.LOG('PLFNG', zLOG.INFO , "__call__() :: REQUEST = %s" % REQUEST)

        if REQUEST == None:
            return None

        else:
           destpath = self._getFSFullPath(PLFNGRelativePath='')

           trimmedFSBasePath = self._getFSBasePath()
           rel_dir = destpath.replace(trimmedFSBasePath, '')
           if rel_dir.startswith('/'): rel_dir = rel_dir[1:]

           #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO ,
           # "__call__():: destpath=%s, FSBasePath=%s, rel_dir=%s" \
           #  % (destpath,trimmedFSBasePath,rel_dir))

           if not rel_dir:
               # We are being visited directly. Redirect to
               # plfng_view here to avoid infinite redirection below.
               dest = make_url(self, 'plfng_view')
               RESPONSE.redirect(dest)
               return

           if os.path.isfile(destpath):
               #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO ,
               #          "__call__() :: %s :: isfile()" % destpath)
               if REQUEST.get('action', '') == 'unpack':
                  self.unpackFile(os.path.dirname(rel_dir),
                                                  destpath,
                                                  REQUEST,
                                                  RESPONSE)

               elif REQUEST.get('action', '') == 'deleteFile':
                  self.deleteFile(rel_dir, destpath, REQUEST, RESPONSE)

               elif REQUEST.get('action', '') == 'catalog':
                  #catalogTool = getToolByName(self, 'portal_catalog')
                  return self.catalogContents()
               elif REQUEST.get('action', '') == 'editMetadata':
                   dest = make_url(self, rel_dir, 'plfng_editMetadata')
                   RESPONSE.redirect(dest)
               else:
                  return self.showFile(destpath, REQUEST, RESPONSE)
           elif os.path.isdir(destpath):
               if hasattr(self, "default_page") and self.default_page:
                   FSDefaultPageFullPath = \
                     os.path.join(destpath, self.default_page)
                   if os.path.exists(FSDefaultPageFullPath):
                       return self.showFile(FSDefaultPageFullPath,
                                            REQUEST,
                                            RESPONSE)

               # Visiting a folder directly may also cause
               # infinite redirection.
               dest = make_url(self, rel_dir, 'plfng_view')
               RESPONSE.redirect(dest)
               return

    def __bobo_traverse__(self, REQUEST, name, RESPONSE=None):
        #zLOG.LOG('PLFNG', zLOG.INFO , "__bobo_traverse__() :: \
        #type(self.REQUEST) = %s" % type(self.REQUEST))
        #zLOG.LOG('PLFNG', zLOG.INFO , "__bobo_traverse__() :: \
        #REQUEST = %s" % REQUEST)
        #zLOG.LOG('PLFNG', zLOG.INFO , "__bobo_traverse__() :: \
        #name = %s" % name)

        if not REQUEST.has_key('_e'):
            REQUEST['_e'] = []

        FSBasePath = self._getFSFullPath(PLFNGRelativePath='')
        destpath = os.path.join(FSBasePath, name)
        if os.path.exists(destpath):
            REQUEST['_e'].append(name)
            return self
        else:
            try: return getattr(self, name)
            except AttributeError: pass
            # Should not raise NotFoundError on __bobo_traverse__.
            # Instead, just return None and let
            # ZPublisher+Acquisition do it's job
            return

    security.declareProtected(ModifyPortalContent, 'addFile')
    def addFile(self, sourceFSfullPath, destPLFNGrelativePath='',
                destBasename=None, moveFile=0, inputMD5=None):
        """ add a file """

        # 1st, make sure that the PLFNG instance is configured with
        # a valid FS folder field value

        if self.validFolder() != 1:
           msg = "addFile() :: Error! validFolder() test failed."
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg )
           return 0

        # make sure that a file was specified

        if not os.path.isfile(sourceFSfullPath):
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: Error! \
           sourceFSfullPath = %s not a file" % sourceFSfullPath )
           return 0

        if not destBasename:
           destBasename = os.path.basename(sourceFSfullPath)

        # make sure destination file name is valid

        checkValidIdResult = checkValidId(destBasename)
        if checkValidIdResult != 1:
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: \
           Error! destination filename (%s) is not permitted: %s" % \
           (destBasename,checkValidIdResult))
           return 0

        # make sure the PLFNG destination relative path is valid

        if destPLFNGrelativePath.startswith('/'):
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: \
           Error! PLFNG destination path (%s) cannot begin with forward \
           slash" % destPLFNGrelativePath)
           return 0

        pathItemList = split(destPLFNGrelativePath,'/')
        for pathItem in pathItemList:
           checkValidIdResult = checkValidId(destBasename)
           if checkValidIdResult != 1:
              zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: \
              Error! PLFNG destination path (%s) invalid: %s" % \
              (destPLFNGrelativePath,checkValidIdResult))
              return 0

        # make sure add operation will not violate quota limit restrictions

        max_allowed_bytes = self.getAvailableQuotaSpace()
        contentLength = 0 # mpg fix this!!!
        if max_allowed_bytes != -1 and contentLength > max_allowed_bytes:
           # uploaded file rejected as it would result in quota limit
           # being exceeded
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: \
           file rejected! CONTENT_LENGTH (%s) + usedBytes(%s) > \
           max_allowed_bytes(%s)" % \
           (contentLength,usedBytes, max_allowed_bytes) )
           return 0

        # if a MD5 checksum was provided, make sure that the
        # server-generated MD5 matches it

        serverMD5 = None
        if inputMD5:
           serverMD5 = generate_md5(sourceFSfullPath,self.external_syscall_md5)
           if inputMD5 != serverMD5:
              zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: \
              file rejected! inputMD5 (%s) != generated MD5 (%s)" % \
              (inputMD5,serverMD5) )
              return 0

        # create destination path as necessary

        FSBasePath = self._getFSFullPath(PLFNGRelativePath='')
        destFSfullPathFolderName = \
          os.path.join(FSBasePath, destPLFNGrelativePath)

        if not os.path.exists(destFSfullPathFolderName):
           try:
              os.makedirs(destFSfullPathFolderName)
           except:
              msg = "addFile() :: Error creating destination path: " + \
                destFSfullPathFolderName
              zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)
              return 0

        # backup existing file as necessary

        destFSfullPath = os.path.join(destFSfullPathFolderName, destBasename)

        if not os.path.exists(destFSfullPath):
           newRevisionNumber = 1

        else:
           # get revision of existing file (or 1 if revision metadata missing)
           oldRevisionNumberText = getMetadataElement(destFSfullPath,
                                                      section="GENERAL",
                                                      option="revision")
           if oldRevisionNumberText:
              oldRevisionNumber = int(oldRevisionNumberText)
           else:
              oldRevisionNumber = 1

           newRevisionNumber = oldRevisionNumber + 1

           # backup existing file if file backup is enabled & \
           # backup_folder path is set
           if self.fileBackup_enabled and self.backup_folder:
              backupdestpath = \
                os.path.join(self.backup_folder, destPLFNGrelativePath)

              if not oldRevisionNumberText:
                 setMetadata(destFSfullPath,
                             section="GENERAL",
                             option="revision",
                             value=oldRevisionNumber)

              # move existing file to backup location, changing its name
              # at the backup location to include trailing rev.#
              backupFileSuffix = '.' + str(oldRevisionNumber)
              backupfilename = os.path.join(backupdestpath, destBasename) + \
                               backupFileSuffix
              # create skeleton dir structure under backupFolder if necessary
              if not os.path.exists(backupdestpath):
                 os.makedirs(backupdestpath)
              shutil.move(destFSfullPath, backupfilename)

        # copy/move file to destination path

        try:
           if moveFile==1:
              shutil.move(sourceFSfullPath, destFSfullPath)
           else:
              shutil.copy(sourceFSfullPath, destFSfullPath)
        except:
           zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "addFile() :: \
           Error! could not add file" )
           return 0

        return newRevisionNumber

    security.declareProtected(ModifyPortalContent, 'HTMLFormUploadFile')
    def HTMLFormUploadFile(self, upload, comment, clientMD5=None):
        """ upload a file via HTML form-based file upload mechanism """

        destpath = self._getFSFullPath(PLFNGRelativePath='')
        trimmedFSBasePath = self._getFSBasePath()
        rel_dir = destpath.replace(trimmedFSBasePath, '')

        # pppffff....some IE browsers apparently do NOT strip the path from
        # the filename on form submittals, so we need to do so here
        if '\\' in upload.filename:
            filename = upload.filename.split('\\')[-1]
        else:
            filename = upload.filename

        uploadFileBaseName = os.path.basename(filename)
        if self.backup_folder:
            backupdestpath = os.path.join(self.backup_folder, rel_dir)
        else:
            backupdestpath = None

        if not upload:
            self.REQUEST.RESPONSE.redirect(self.REQUEST['URL1']+\
              '/plfng_view?portal_status_message=no file was uploaded!')
            return 0

        if self.require_MD5_with_upload and not clientMD5:
            msg = 'you MUST provide the MD5 checksum for the file you want \
            to upload!'
            self.REQUEST.RESPONSE.redirect(self.REQUEST['URL1']+\
              '/plfng_view?portal_status_message=' + msg)
            return 0

        destFSfullPath = os.path.join(destpath, os.path.basename(filename))
        tmpfile = destFSfullPath + '.plfngtmp'
        f = open(tmpfile, 'wb')
        f.write(upload.read())
        f.close()
        serverMD5 = None

        newRevisionNumber = \
         self.addFile(sourceFSfullPath=tmpfile,
                     destPLFNGrelativePath=rel_dir,
                     destBasename=os.path.basename(destFSfullPath),
                     moveFile=1,
                     inputMD5=clientMD5)

        if newRevisionNumber == 0:
           os.remove(tmpfile)
           self.REQUEST.RESPONSE.redirect(self.REQUEST['URL1']+\
             '/plfng_view?portal_status_message=file rejected.')
        else:

           # ------------------------- apply metadata -------------------------
           # GENERAL:
           #   comments    - comments on the file
           #   description - (tbd)
           #   source      - userId of the source/uploader/provider
           #   language    - language code for the file contents
           #   revision    - the PLFNG centric revision # of this file
           # DIAGNOSTICS:
           #   md5         - server-validated md5 checksum of this file
           # ARCHIVEINFO:
           #   numUnpackedFiles   - # files that the packed file contains
           #   sizezUnpackedFiles - total # bytes for all of the unpacked files
           # CHANGELOG:
           #   history     - (tbd)
           # ------------------------------------------------------------------

           # GENERAL: 'comments' option
           if comment:
               setMetadata(destFSfullPath,
                           section="GENERAL",
                           option="comment",
                           value=comment)

           # GENERAL: 'source' option
           portal = getToolByName(self, 'portal_url').getPortalObject()
           portal_membership = getToolByName(portal, 'portal_membership')
           if portal_membership.isAnonymousUser():
               creator = 'anonymous'
           else:
               creator = portal_membership.getAuthenticatedMember().getId()
           setMetadata(destFSfullPath,
                       section="GENERAL",
                       option="source",
                       value=creator)

           # GENERAL: 'revision' option
           setMetadata(destFSfullPath,
                       section="GENERAL",
                       option="revision",
                       value=newRevisionNumber)

           # DIAGNOSTICS: 'md5' option
           if clientMD5:
               setMetadata(destFSfullPath,
                           section="DIAGNOSTICS",
                           option="md5",
                           value=clientMD5)

           # if .zip file, set ARCHIVEINFO metadata
           if self.mimetypes_registry.classify(data=None, \
             filename=filename.lower()) == 'application/zip':
               setZipInfoMetadata(filename)

           self.REQUEST.RESPONSE.redirect(self.REQUEST['URL1']+\
             '/plfng_view?portal_status_message=file added.')

    security.declareProtected(ModifyPortalContent, 'create_directory')
    def create_directory(self, dirname, REQUEST):
        """ create a sub-directory """
        dirname = dirname.replace('\\','/')
        if dirname.startswith('/') or dirname.find('..') > -1 or \
           dirname.find(':') > -1:
            msg="create directory aborted: illegal directory name: " + dirname
            zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg )
            REQUEST.RESPONSE.redirect(REQUEST['URL1']+\
              '/plfng_view?portal_status_message=' + msg)
            return 0

        FSBasePath = self._getFSFullPath(PLFNGRelativePath='')
        destpath = os.path.join(FSBasePath, dirname)

        print destpath
        if os.path.exists(destpath):
            raise ValueError('Directory %s already exists' % dirname)

        # try..except to avoid exposing the realworld path
        try:
            os.makedirs(destpath)
        except:
            raise RuntimeError('Directory could not be created')

        url = '/' + os.path.join(self.absolute_url(1), rel_dir, dirname) +\
         '/plfng_view?portal_status_message=Directory created'
        REQUEST.RESPONSE.redirect(url)

        security.declareProtected('View', 'getProperties')
    def getProperties(self, REQUEST=None):
        """ get the summary properties for the local filesystem directory
            for this class instance """

        FSFullPath = self._getFSFullPath(PLFNGRelativePath='')

        #msg = 'getProperties() :: calling _getFolderProperties('+FSfullPath+')'
        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)

        localfolder_props = _getFolderProperties(FSFullPath)

        return localfolder_props

    security.declareProtected('View', 'get_size')
    def get_size(self):
        """ return the size of the underlying contents """

        if self.validFolder():
           trimmedFSBasePath = self._getFSBasePath()
           localfolder_props = _getFolderProperties(trimmedFSBasePath)
           return localfolder_props.get('size',0)
        else:
           return 0

    security.declareProtected(ModifyPortalContent, 'unpackFile')
    def unpackFile(self, plfngRelativeDir, FSpackedFile, REQUEST, RESPONSE):
        """ unpack a file """

        # for now, unzip is the only type of unpacking implemented

        # 1st, make sure the file is an unpackable type
        if not self.mimetypes_registry.classify(data=None,
                                                filename=FSpackedFile.lower())\
                                                == 'application/zip':
            RESPONSE.redirect(REQUEST['URL1']+\
              '/plfng_view?portal_status_message=file cannot be unpacked \
              (not a recognized packed file type).')
            return 0
        # then, make sure the file unpacking property is set
        elif not self.allow_file_unpacking:
            msg = 'file unpacking is not allowed here.'
            RESPONSE.redirect(REQUEST['URL1']+\
              '/plfng_view?portal_status_message=' + msg)
            return 0
        # then, check that file unpacking will not violate any quota-limits
        elif self.quota_aware:
            # traverse up the acquisition tree looking for first container with
            # a non-zero 'quota_maxbytes' attribute.  If such a container is
            # found, find out the total number of bytes used by the contents of
            # this container in order to determine if the addition of the
            # unpacked contents of the file will exceed quota_maxbytes --in
            # which case do not carry out the unpack operation.

            max_allowed_bytes = 0

            for parent in self.aq_chain[1:]:
               if hasattr(parent, "quota_maxbytes"):
                  max_allowed_bytes = int(getattr(parent, "quota_maxbytes"))
                  if max_allowed_bytes > 0:
                     usedBytes = determine_bytes_usage(parent)
                     break

            try:
               unpackedSize = int(getMetadataElement(FSpackedFile,
                                                     section="ARCHIVEINFO",
                                                     option="unpacked_size"))
            except:
               try:
                  setZipInfoMetadata(FSpackedFile)
                  unpackedSize = int(getMetadataElement(FSpackedFile,
                                                        section="ARCHIVEINFO",
                                                        option="unpacked_size")
                                                        )
               except:
                  msg = 'file could not be unpacked (not a valid file?!).'
                  RESPONSE.redirect(REQUEST['URL1']+\
                    '/plfng_view?portal_status_message=' + msg)
                  return 0
            if max_allowed_bytes > 0 and \
             (unpackedSize + usedBytes) > max_allowed_bytes:
               msg = 'file cannot be unpacked as doing so would violate \
               quota limit.'
               REQUEST.RESPONSE.redirect(REQUEST['URL1']+\
                 '/plfng_view?portal_status_message=' + msg)
               zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "unpackFile() :: \
               unpack rejected! unpackedSize (%s) + usedBytes(%s) > \
               max_allowed_bytes(%s)" % \
               (unpackedSize,usedBytes, max_allowed_bytes) )
               return 0
        # if we made it to this point, unpack the file
        if self.backup_folder:
            backupdestpath = os.path.join(self.backup_folder, plfngRelativeDir)
        else:
            backupdestpath = None

        if upzipFile(FSfilename=FSpackedFile,
                     FSBackupFolderBase=backupdestpath):
            RESPONSE.redirect(REQUEST['URL1']+\
              '/plfng_view?portal_status_message=file unpacked.')
            return 1
        else:
            RESPONSE.redirect(REQUEST['URL1']+\
              '/plfng_view?portal_status_message=file could not be unpacked.')
            return 0




    security.declareProtected('Delete objects', 'deleteFile')
    def deleteFile(self, rel_dir, fileToDelete, REQUEST, RESPONSE):
        """ delete the file """

        if not os.path.exists(fileToDelete):
           return 0
        else:
           # move file to backupFolder if file backup is enabled &
           # backup_folder path is set
           if self.fileBackup_enabled and self.backup_folder:
               # get revision of existing file (or 1 if rev. metadata missing)
               oldRevisionNumberText = \
                 getMetadataElement(fileToDelete,
                                    section="GENERAL",
                                    option="revision")
               if oldRevisionNumberText:
                   oldRevisionNumber = int(oldRevisionNumberText)
               else:
                   oldRevisionNumber = 1
                   # uncomment the next statement to update the file's
                   # metadata if its also going to be backed up
                   #setMetadata(fileToDelete, section="GENERAL", \
                   #  option="revision", value=oldRevisionNumber)

               # move existing file to backup location, changing its name
               # at the backup location to include trailing rev.#
               backupdestpath = \
                 os.path.dirname(os.path.join(self.backup_folder,rel_dir))
               backupFileSuffix = '.' + str(oldRevisionNumber)
               backupfilename = \
                 os.path.join(backupdestpath, os.path.basename(fileToDelete))\
                   + backupFileSuffix
               # create skeleton dir structure under backupFolder if necessary
               if not os.path.exists(backupdestpath):
                   os.makedirs(backupdestpath)
               shutil.move(fileToDelete, backupfilename)
           else:
               os.remove(fileToDelete)

           metadataFileToDelete = fileToDelete + '.metadata'
           if os.path.exists(metadataFileToDelete):
               os.remove(metadataFileToDelete)

           RESPONSE.redirect(REQUEST['URL1']+\
             '/plfng_view?portal_status_message=' + rel_dir + ' deleted.')
           return 1

    security.declareProtected('Delete objects', 'deleteFolder')
    def deleteFolder(self, rel_dir, folderToDelete, REQUEST):
        """ delete the folder """
        shutil.rmtree(folderToDelete)
        REQUEST.RESPONSE.redirect(REQUEST['URL2']+\
          '/plfng_view?portal_status_message=' + rel_dir + ' deleted.')
        return 1

    def catalogContents(self,rel_dir=None, catalog='portal_catalog'):
        filesCataloged = 0
        filesNotCataloged = 0
        filetypePhrasesSkipList = []
        meta_type = "FileProxy"
        # set View permission for all cataloged files to that of PLFNG object
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

        FSfullPathFolderName = self._getFSFullPath(PLFNGRelativePath=rel_dir)

        uidBase = str('/' + portalId + '/'+ \
                  this_portal.getRelativeContentURL(self) + '/')

        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: \
        #FSfullPathFolderName=%s " % FSfullPathFolderName )
        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: \
        #rel_dir=%s" % rel_dir )
        #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "catalogContents() :: \
        #portal path=%s" % this_portal.getRelativeContentURL(self) )

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

    security.declareProtected(CMFCorePermissions.View,
                              'getAddressDisplayStyleVocab')
    def getAddressDisplayStyleVocab(self):
        return DisplayList(
           (
            ('PLFNG_Base_Relative','PLFNG_Base_Relative'),
           ))

    security.declareProtected('View', 'getFilteredContents')
    def getFilteredContents(self,rel_dir=None):
        """ list filtered content of local filesystem """

        filteredFileList = []
        filteredFolderList = []
        resultList = []

        if rel_dir == None: rel_dir = ''
        destpath = self._getFSFullPath(PLFNGRelativePath=rel_dir)

        if rel_dir == '':
           outputPrefix = ''
        else:
           outputPrefix = rel_dir.replace('\\', '/') + '/'

        this_portal = getToolByName(self, 'portal_url')
        mimetypesTool = getToolByName(this_portal, 'mimetypes_registry')

        filePrefixesSkip = self._getAttribute('hidden_file_prefixes')
        fileSuffixesSkip = self._getAttribute('hidden_file_suffixes')
        fileNamesSkip = self._getAttribute('hidden_file_names')
        folderPrefixesSkip = self._getAttribute('hidden_folder_prefixes')
        folderSuffixesSkip = self._getAttribute('hidden_folder_suffixes')
        folderNamesSkip = self._getAttribute('hidden_folder_names')
        trimmedFolderBasePath = os.path.normpath(destpath)

        filteredFileList, filteredFolderList = \
           getFilteredFSItems(FSfullPath=trimmedFolderBasePath,
                                 skipInvalidIds=1,
                                 mimetypesTool=mimetypesTool,
                                 filetypePhrasesSkipList=[],
                                 filePrefixesSkipList=filePrefixesSkip,
                                 fileSuffixesSkipList=fileSuffixesSkip,
                                 fileNamesSkipList=fileNamesSkip,
                                 folderPrefixesSkipList=folderPrefixesSkip,
                                 folderSuffixesSkipList=folderSuffixesSkip,
                                 folderNamesSkipList=folderNamesSkip)

        for filename in filteredFileList:
           resultList.append(outputPrefix + filename)

        for subFolder in filteredFolderList:
           resultList.append(outputPrefix + subFolder+'/')
           new_rel_dir = os.path.join(rel_dir,subFolder)
           sub_resultList = self.getFilteredContents(rel_dir=new_rel_dir)
           resultList = resultList + sub_resultList

        return resultList

    security.declareProtected('View', 'getFilteredOutContents')
    def getFilteredOutContents(self,rel_dir=None):
        """ list filtered out content of local filesystem """

        illegalFilesList = []
        filteredOutFileList = []
        filteredOutFolderList = []

        filteredFileList = []
        filteredFolderList = []

        if rel_dir == None: rel_dir = ''
        destpath = self._getFSFullPath(PLFNGRelativePath=rel_dir)

        this_portal = getToolByName(self, 'portal_url')
        mimetypesTool = getToolByName(this_portal, 'mimetypes_registry')

        filePrefixesSkip = self._getAttribute('hidden_file_prefixes')
        fileSuffixesSkip = self._getAttribute('hidden_file_suffixes')
        fileNamesSkip = self._getAttribute('hidden_file_names')
        folderPrefixesSkip = self._getAttribute('hidden_folder_prefixes')
        folderSuffixesSkip = self._getAttribute('hidden_folder_suffixes')
        folderNamesSkip = self._getAttribute('hidden_folder_names')

        trimmedFolderBasePath = os.path.normpath(destpath)

        illegalFilesList, illegalFoldersList, filteredOutFileList, \
           filteredOutFolderList = \
           getFilteredOutFSItems(FSfullPath=trimmedFolderBasePath,
                              PLFNGrelPath=rel_dir,
                              skipInvalidIds=1,
                              mimetypesTool=mimetypesTool,
                              filetypePhrasesSkipList=[],
                              filePrefixesSkipList=filePrefixesSkip,
                              fileSuffixesSkipList=fileSuffixesSkip,
                              fileNamesSkipList=fileNamesSkip,
                              folderPrefixesSkipList=folderPrefixesSkip,
                              folderSuffixesSkipList=folderSuffixesSkip,
                              folderNamesSkipList=folderNamesSkip)

        filteredFileList, filteredFolderList = \
           getFilteredFSItems(FSfullPath=trimmedFolderBasePath,
                                 skipInvalidIds=1,
                                 mimetypesTool=mimetypesTool,
                                 filetypePhrasesSkipList=[],
                                 filePrefixesSkipList=filePrefixesSkip,
                                 fileSuffixesSkipList=fileSuffixesSkip,
                                 fileNamesSkipList=fileNamesSkip,
                                 folderPrefixesSkipList=folderPrefixesSkip,
                                 folderSuffixesSkipList=folderSuffixesSkip,
                                 folderNamesSkipList=folderNamesSkip)

        for subFolder in filteredFolderList:
           new_rel_dir = os.path.join(rel_dir,subFolder)
           sub_illegalFilesList, sub_illegalFoldersList, \
              sub_filteredOutFileList, sub_filteredOutFolderList = \
              self.getFilteredOutContents(rel_dir = new_rel_dir)

           illegalFilesList = illegalFilesList + sub_illegalFilesList
           illegalFoldersList = illegalFoldersList + sub_illegalFoldersList
           filteredOutFileList = \
              filteredOutFileList + sub_filteredOutFileList
           filteredOutFolderList = \
              filteredOutFolderList + sub_filteredOutFolderList

        return illegalFilesList, illegalFoldersList, \
               filteredOutFileList, filteredOutFolderList


def _getFolderProperties(FSfullPathFolderName):

   filteredFileList = []
   filteredFolderList = []
   bytesInFolder = 0
   folderCount = 0
   fileCount = 0

   #msg = '_getFolderProperties() :: calling getFilteredFSItems() :\
   # FSfullPath = ' + FSfullPathFolderName
   #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)

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

      #msg = '_getFolderProperties() :: calling _getFolderProperties('+subfolderFullName+')'
      #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , msg)

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



