import os
import shutil
import string
import re
from types import StringType, UnicodeType
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from ConfigParser import ConfigParser
from Acquisition import aq_base
import zipfile

import zLOG

import md5

from FileProxy import FileProxy

MD5_LENGTH = 32

# Note: Optional support for an external md5 generation system utility 
# has only been tested with the following utility:
#   * md5: md5deep v1.2 (http://md5deep.sourceforge.net/)

security = ClassSecurityInfo()

bad_id=re.compile(r'[^a-zA-Z0-9-_~,.$\(\)# ]').search

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'setMetadata')
def setMetadata(filename, section, option, value):

   metadataFileName = filename+".metadata"
   
   metadataFileParser = ConfigParser()
   metadataFileParser.read(metadataFileName)
   if not metadataFileParser.has_section(section):
      metadataFileParser.add_section(section)
   metadataFileParser.set(section,option,value)
   try:
      fp = open( metadataFileName, 'w')
      metadataFileParser.write(fp)
      fp.close()
      return 1
   except:
      return 0    

# --------------------------------------------------------------------
security.declarePublic('getMetadataElement')
def getMetadataElement(filename,section,option):
   metadataFileName = filename+".metadata"
   if os.path.exists(metadataFileName):
      try:
         metadataFileParser = ConfigParser()
         metadataFileParser.read(metadataFileName)
         return metadataFileParser.get(section,option)
      except:
         #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
         # "getMetadataElement(%s,%s,%s)=None" % (section,option,filename))
         return None
   else:
      return None

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'getZipInfo')
def getZipInfo(filename):

   filename = fixDOSPathName(filename)
   
   z = zipfile.ZipFile(filename) 
   
   uncompressedSize = 0.0
   compressedSize = 0.0
   for zinfo in z.filelist:
      uncompressedSize = uncompressedSize + zinfo.file_size
      compressedSize = compressedSize + zinfo.compress_size
   
   if uncompressedSize > 1.0:
      compressionRatio = 100.0 * (1.0 - compressedSize/uncompressedSize)
   else:
      compressionRatio = 0.0
   
   return len(z.filelist), uncompressedSize
   
   # here is the code to mimic 'unzip -Zt' output
   # result = "%d files, %d bytes uncompressed, %d bytes compressed: %.1f%%"
   #    % (len(z.filelist), uncompressedSize, compressedSize, compressionRatio)
   
   # this is the code from PLFNG 0.5 that used an external system
   # call to the UnZip v5.50 utility.  Here is its output format: 
   #  21 files, 50550 bytes uncompressed, 12409 bytes compressed:  75.5%
   # -------------------------------------------------------------
   #SYSCALL_ZIPINFO         = "c:\\plone-utils\\unzip -Zt"
   #syscall = "%s %s" % (SYSCALL_ZIPINFO,syscall_filename)
   #process_fp = os.popen(syscall)
   #result = process_fp.read()
   # -------------------------------------------------------------   


# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'setZipInfoMetadata')
def setZipInfoMetadata(filename):

   if zipfile.is_zipfile(filename): 
      num_files, unpacked_size = getZipInfo(filename)
  
      setMetadata(filename,
                  section="ARCHIVEINFO",
                  option="num_files",
                  value=num_files)
      setMetadata(filename,
                  section="ARCHIVEINFO",
                  option="unpacked_size",
                  value=unpacked_size)
      return 1

   else:
      return 0

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'upzipFile') 
def upzipFile(FSfilename, FSBackupFolderBase=None):
   # this method does the same thing as the following system call:
   # SYSCALL_UNZIP = "c:\\plone-utils\\unzip -o -d"
   # syscall = "%s %s %s" % (SYSCALL_UNZIP,todir,syscall_filename)
   # result = os.system(syscall)

   FSfilename = fixDOSPathName(FSfilename)
   todir = os.path.dirname(FSfilename)
   
   if zipfile.is_zipfile(FSfilename): 

      z = zipfile.ZipFile(FSfilename)

      # create the extract directory structure before extracting files to it
      for zitem in z.namelist():
         if zitem.endswith('/'):
            newDirectoryName = os.path.join(todir, zitem)
            if not os.path.exists(newDirectoryName):
                os.makedirs(newDirectoryName)

      # extract the files from the zipfile
      for zitem in z.namelist():
         if not zitem.endswith('/'):
            checkValidIdResult = checkValidId(os.path.basename(zitem))
            if checkValidIdResult != 1:
               zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
                 "upzipFile() :: checkValidId(%s) failed:: %s" \
                 % (zitem,checkValidIdResult) ) 
            else:
               tofile = os.path.join(todir, zitem)
               oldRevisionNumber = 0
               newRevisionNumber = 1
               # if file already exists, back it up to 
               # FSBackupFolderBase if specified
               if os.path.exists(tofile) and FSBackupFolderBase:
                  # get revision of existing file 
                  # (or 1 if revision metadata missing)
                  oldRevisionNumberText = getMetadataElement(tofile,
                                                             section="GENERAL",
                                                             option="revision")
                  if oldRevisionNumberText:
                      oldRevisionNumber = int(oldRevisionNumberText)
                  else:
                      oldRevisionNumber = 1
   
                  # move existing file to backup location renamed with trailing rev.#
                  backupdestpath = \
                     os.path.dirname(os.path.join(FSBackupFolderBase,zitem))
                  backupFileSuffix = '.' + str(oldRevisionNumber)
                  backupfilename = \
                     os.path.join(backupdestpath, os.path.basename(zitem)) + \
                        backupFileSuffix
                  # create skeleton directory structure under 
                  # backupFolder if necessary 
                  if not os.path.exists(backupdestpath):
                     os.makedirs(backupdestpath)
                  shutil.move(tofile, backupfilename)
                  #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
                  #"upzipFile() move(%s, %s)" % (tofile,backupfilename))
               
               # extract the file
               f = open(tofile, 'wb')
               f.write(z.read(zitem))
               f.close()
   
               # set/update metadata 
               newRevisionNumber = oldRevisionNumber + 1
               setMetadata(tofile,
                           section="GENERAL",
                           option="revision",
                           value=newRevisionNumber)

      #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
      #"upzipFile() finished unzip'ing %s" % FSfilename)
      return 1

   else:
      zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
               "upzipFile() ABORTED: %s not a valid zip file." % FSfilename )
      return 0    

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'generate_md5')
def generate_md5(filename,syscallcommand='none'):

   filename = fixDOSPathName(filename)
   md5_hexvalue = ''

   if syscallcommand == 'none':
      m = md5.new()
      blocksize = 2<<16
      try:
         fobj = open(filename, 'rb')
         while True:
             chunk = fobj.read(blocksize)
             if not chunk:
                 break
             m.update(chunk)
         md5_hexvalue = m.hexdigest()
         fobj.close()
      except:
         md5_hexvalue = ''    

   else:
      fullsyscall = "%s %s" % (syscallcommand,filename)
      process_fp = os.popen(fullsyscall)
      md5_hexvalue = process_fp.read()[:MD5_LENGTH]

   if len(md5_hexvalue) == MD5_LENGTH:
      return md5_hexvalue
   else:
      # failure should throw an exception, but for now, return 
      # easily identified bogus checksum 
      return "99999999999999999999999999999999"

# --------------------------------------------------------------------
def determine_bytes_usage(startObject):
    """ 
        attempt to determine the total size in bytes of all subobjects of 
        object.  Note: this only gathers sizes of objects that have the 
        'get_size' attribute.
    """
    # not used now, but might come in handy at some point
    exclude_quota_objects = []
    
    obj_sizes = [ obj.get_size() for id, \
       obj in startObject.ZopeFind( startObject, search_sub=1 ) \
       if hasattr( aq_base( obj ), 'get_size') and \
       getattr( obj, 'meta_type', None ) not in exclude_quota_objects ]
    if obj_sizes:
        objects_size = int( reduce( lambda x,y: x+y, obj_sizes ) )
    else:
        objects_size = 0

    return objects_size

# --------------------------------------------------------------------
def fixDOSPathName(srcFileName):
    fixedName=string.join(string.split(srcFileName,'\\'),'\\\\')
    fixedName=string.join(string.split(fixedName,'\t'),'\\\\t')
    fixedName=string.join(string.split(fixedName,'\n'),'\\\\n')
    return fixedName

# --------------------------------------------------------------------
def checkValidId(id):
    # this is essentially checkValidId() from OFS/OBjectManager.py

    if not id:
        return 'The id is invalid because it is empty or not specified'
    if bad_id(id) is not None:
        return \
        'The id is invalid because it contains characters illegal in URLs.'
    if id in ('.', '..'):
        return 'The id is invalid because it is not traversable.'
    if id.startswith('_'):
        return 'The id is invalid because it begins with an underscore.'
    if id.startswith('aq_'):
        return 'The id is invalid because it begins with "aq_".'
    if id.endswith('__'):
        return 'The id is invalid because it ends with two underscores.'
    if id == 'REQUEST':
        return 'The id is invalid because REQUEST is a reserved name.'
    if '/' in id:
        return 'The id is invalid because it contains "/" characters illegal in URLs.'
    return 1

# --------------------------------------------------------------------
def catalogFSContent(FSfullPath, filetypePhrasesSkipList, catalogTool, 
                     mimetypesTool, uidBase, view_roles, effective, expires,
                     meta_type):
   
   #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
   #   "catalogFSContent(%s,%s,%s,%s,%s,%s,%s,%s,%s)" \
   #   % (FSfullPath, filetypePhrasesSkipList, catalogTool, mimetypesTool, \
   #    uidBase, view_roles, effective, expires, meta_type) )

   # uidBase = str('/' + portalId + '/'+ \
   # this_portal.getRelativeContentURL(self) + '/')
   
   filesCataloged = 0

   fileSuffixesSkipList=['.metadata','.plfngtmp']
   
   # 1st, get the filtered lists of files and folders to catalog
   filteredFileList = []
   filteredFolderList = []
   
   if os.path.isdir(FSfullPath):
      FSfullPathFolderName = FSfullPath
      
      filteredFileList, filteredSubfolderItems = \
         getFilteredFSItems(FSfullPath=FSfullPathFolderName, 
                            skipInvalidIds=1, 
                            mimetypesTool=mimetypesTool, 
                            filetypePhrasesSkipList=filetypePhrasesSkipList, 
                            filePrefixesSkipList=[], 
                            fileSuffixesSkipList=fileSuffixesSkipList, 
                            fileNamesSkipList=[],
                            folderPrefixesSkipList=[], 
                            folderSuffixesSkipList=[], 
                            folderNamesSkipList=[])
   else:
      FSfullPathFolderName = os.path.basename(FSfullPath)
      FSfullPathFileName = FSfullPath
      fileName = os.path.basename(FSfullPathFileName)
      
      skipThisItem = 0
      checkValidIdResult = checkValidId(fileName)
      if checkValidIdResult != 1: 
         skipThisItem = 1
         zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
         "catalogFSContent() :: checkValidId(%s) failed:: %s" \
         % (FSfullPathFileName,checkValidIdResult) )
      for suffix in fileSuffixesSkipList:
         if fileName.endswith(suffix): 
            skipThisItem = 1
            break

      if skipThisItem != 1:
         filteredFileList.append(fileName)
   
   # instantiate a barebones FileProxy instance
   dummyFileProxy = FileProxy(id="dummy",
                              filepath=FSfullPath,
                              fullname="dummy",
                              properties=None)
   dummyFileProxy.meta_type = meta_type
   dummyFileProxy.effective = effective
   dummyFileProxy.expires = expires 
      
   # catalog all of the files in the filtered file list
   for fileItem in filteredFileList:
      FSfullPathFileName = os.path.join(FSfullPathFolderName, fileItem)

      uid = str(uidBase +  os.path.basename(FSfullPathFileName))
      dummyFileProxy.id = str(fileItem)
      dummyFileProxy.url = FSfullPathFileName
      dummyFileProxy.encoding = None
      mi = mimetypesTool.classify(data=None, filename=fileItem.lower())
      try:
         item_mime_type = mi.normalized()
      except:
         item_mime_type = mimetypesTool.defaultMimetype
         #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
         #         "warning: no filename mime type for %s" % filename)
      dummyFileProxy.mime_type = item_mime_type

      try:
          iconPath = mi.icon_path
      except:
          iconPath = 'unknown.png'

      dummyFileProxy.setIconPath(iconPath)

      #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
      #"catalogContents() :: file=%s" % FSfullPathFileName )
      #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
      #"catalogContents() :: mimetype=%s" % dummyFileProxy.mime_type )
      #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
      #"catalogContents() :: catalog uid=%s" % uid )
                 
      catalogTool.catalog_object( dummyFileProxy, uid )
                   
      filesCataloged = filesCataloged + 1
   
   # catalog all the contents of the subfolders in the filtered subfolders list
   for subfolder in filteredSubfolderItems:
      subfolderFullName = os.path.join(FSfullPathFolderName, subfolder)
      #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
      #"catalogFSContent() :: subdir=%s" % subfolderFullName )
      newUidBase = uidBase + subfolder + '/'
      subfolderfilesCataloged = \
         catalogFSContent(subfolderFullName, filetypePhrasesSkipList, 
                          catalogTool, mimetypesTool, newUidBase, view_roles,
                          effective, expires, meta_type)
      filesCataloged = filesCataloged + subfolderfilesCataloged

   return filesCataloged


# --------------------------------------------------------------------
def getFilteredFSItems(FSfullPath, skipInvalidIds, mimetypesTool, 
                       filetypePhrasesSkipList, filePrefixesSkipList,
                       fileSuffixesSkipList, fileNamesSkipList,
                       folderPrefixesSkipList, folderSuffixesSkipList,
                       folderNamesSkipList):
   
   # this method returns the filteredFileList & filteredFolderList children of 
   # the specified filesystem (FS) path
   
   filteredFileList = []
   filteredFolderList = []
   
   if not os.path.exists(FSfullPath):
      # raise exception here?
      zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
      "getFilteredFSItems() :: FSfullPath not found (%s)" % FSfullPath )
      
   else:   
      try:
         rawItemList = os.listdir(FSfullPath)
      except:
         zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
         "getFilteredFSItems() :: error reading folder (%s) contents" \
         % FSfullPath )
         return filteredFileList, filteredFolderList

      for item in rawItemList:
         if skipInvalidIds:
            checkValidIdResult = checkValidId(item)
            if checkValidIdResult != 1: 
               #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
               #"getFilteredFSItems() :: checkValidId(%s) failed:: %s" \
               #% (item,checkValidIdResult) )
               continue
      
         FSfullPathItemName = os.path.join(FSfullPath, item)
         skipThisItem = 0
         
         if os.path.isdir(FSfullPathItemName):
             
             for prefix in folderPrefixesSkipList:
                if item.startswith(prefix): 
                   skipThisItem = 1
                   break
             
             for suffix in folderSuffixesSkipList:
                if item.endswith(suffix): 
                   skipThisItem = 1
                   break
             
             for completeName in folderNamesSkipList:
                if item == completeName: 
                   skipThisItem = 1
                   break
             
             if not skipThisItem: 
                filteredFolderList.append(item)
         
         else:
             
             if mimetypesTool:
                mi = mimetypesTool.classify(data=None, filename=item.lower())
                try:
                   item_mime_type = mi.normalized()
                except:
                   item_mime_type = mimetypesTool.defaultMimetype
                   #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
                   # "warning: no filename mime type for %s" % filename)
             
                for filetypePhrase in filetypePhrasesSkipList:
                   if item_mime_type.find(filetypePhrase) >= 0:
                      skipThisItem=1
                      break
             
             for prefix in filePrefixesSkipList:
                if item.startswith(prefix): 
                   skipThisItem = 1
                   break
             
             for suffix in fileSuffixesSkipList:
                if item.endswith(suffix): 
                   skipThisItem = 1
                   break
             
             for completeName in fileNamesSkipList:
                if item == completeName: 
                   skipThisItem = 1
                   break
             
             if not skipThisItem: 
                filteredFileList.append(item)
     
   #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
   #"filteredFolderList= %s" % filteredFolderList)
   #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "filteredFileList= %s" \
   #% filteredFileList)
   
   return filteredFileList, filteredFolderList
   
   
# --------------------------------------------------------------------
def getFilteredOutFSItems(FSfullPath, PLFNGrelPath, skipInvalidIds,
                          mimetypesTool, filetypePhrasesSkipList, 
                          filePrefixesSkipList, fileSuffixesSkipList,
                          fileNamesSkipList,folderPrefixesSkipList,
                          folderSuffixesSkipList, folderNamesSkipList):
   
   # this method is the inverse of the getFilteredFSItems().  It returns
   # the file and folder children of the specified filesystem (FS) path
   # that are ***NOT*** returned by the getFilteredFSItems() method
   
   if PLFNGrelPath != '':
      PLFNGrelPath = PLFNGrelPath.replace('\\', '/') + '/'

   illegalFilesList = []
   illegalFoldersList = []
   filteredOutFileList = []
   filteredOutFolderList = []
   
   if not os.path.exists(FSfullPath):

      # raise exception here?
      zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
      "getFilteredOutFSItems() :: FSfullPath not found (%s)" % FSfullPath )
      
   else:   
      try:
         rawItemList = os.listdir(FSfullPath)
      except:
         zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
         "getFilteredOutFSItems() :: error reading folder (%s) contents" \
         % FSfullPath )
         return filteredFileList, filteredFolderList

      for item in rawItemList:
         FSfullPathItemName = os.path.join(FSfullPath, item)
         skipThisItem = 0
         
         if os.path.isdir(FSfullPathItemName):
             checkValidIdResult = checkValidId(item)
             if skipInvalidIds and checkValidIdResult != 1:
                illegalFoldersList.append(PLFNGrelPath+item)
                #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
                #"getFilteredOutFSItems() :: checkValidId(%s) failed:: %s" \
                #% (item,checkValidIdResult) )
             else:
                for prefix in folderPrefixesSkipList:
                   if item.startswith(prefix): 
                      skipThisItem = 1
                      break
                
                for suffix in folderSuffixesSkipList:
                   if item.endswith(suffix): 
                      skipThisItem = 1
                      break
                
                for completeName in folderNamesSkipList:
                   if item == completeName: 
                      skipThisItem = 1
                      break
                
                if skipThisItem: 
                   filteredOutFolderList.append(PLFNGrelPath+item)
         
         else:
             checkValidIdResult = checkValidId(item)
             if skipInvalidIds and checkValidIdResult != 1:
                illegalFilesList.append(PLFNGrelPath+item)
                #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
                #"getFilteredOutFSItems() :: checkValidId(%s) failed:: %s" \
                #% (item,checkValidIdResult) )
             
             else:
                if mimetypesTool:
                   mi = mimetypesTool.classify(data=None,filename=item.lower())
                   try:
                      item_mime_type = mi.normalized()
                   except:
                      item_mime_type = mimetypesTool.defaultMimetype
                      #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
                      # "warning: no filename mime_type for %s" % filename)
                
                   for filetypePhrase in filetypePhrasesSkipList:
                      if item_mime_type.find(filetypePhrase) >= 0:
                         skipThisItem=1
                         break
                
                for prefix in filePrefixesSkipList:
                   if item.startswith(prefix): 
                      skipThisItem = 1
                      break
                
                for suffix in fileSuffixesSkipList:
                   if item.endswith(suffix): 
                      skipThisItem = 1
                      break
                
                for completeName in fileNamesSkipList:
                   if item == completeName: 
                      skipThisItem = 1
                      break
             
                if skipThisItem: 
                   filteredOutFileList.append(PLFNGrelPath+item)
     
   #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
   #"filteredOutFolderList= %s" % filteredOutFolderList)
   #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , \
   #"filteredOutFileList= %s" % filteredOutFileList)
   
   return illegalFilesList, illegalFoldersList,\
          filteredOutFileList, filteredOutFolderList   