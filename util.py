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
         return None
         #raise 'Metadata Not Found', 'Could not retrieve metadata %s:%s for the file %s.' % (section,option,filename)
   else:
      return None
# --------------------------------------------------------------------
security.declarePublic('getMetadataElements')
def getMetadataElements(filename,section):
   metadataFileName = filename+".metadata"
   try:
      metadataFileParser = ConfigParser()
      metadataFileParser.read(metadataFileName)
      return metadataFileParser.items(section,option)
   except:
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
   #         % (len(z.filelist), uncompressedSize, compressedSize, compressionRatio)
   
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
  
      setMetadata(filename, section="ARCHIVEINFO", option="num_files", value=num_files)
      setMetadata(filename, section="ARCHIVEINFO", option="unpacked_size", value=unpacked_size)
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
         checkValidIdResult = checkValidId(zitem)
         if checkValidIdResult != 1:
            zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upzipFile() :: checkValidId(%s) failed:: %s" % (zitem,checkValidIdResult) ) 
         else:
            if not zitem.endswith('/'):
               tofile = os.path.join(todir, zitem)
               oldRevisionNumber = 0
               newRevisionNumber = 1
               # if file already exists, back it up to FSBackupFolderBase if specified
               if os.path.exists(tofile) and FSBackupFolderBase:
                  # get revision of existing file (or 1 if revision metadata missing)
                  oldRevisionNumberText = getMetadataElement(tofile, section="GENERAL", option="revision")
                  if oldRevisionNumberText:
                      oldRevisionNumber = int(oldRevisionNumberText)
                  else:
                      oldRevisionNumber = 1
   
                  # move existing file to backup location renamed with trailing rev.#
                  backupdestpath = os.path.dirname(os.path.join(FSBackupFolderBase,zitem))
                  backupFileSuffix = '.' + str(oldRevisionNumber)
                  backupfilename = os.path.join(backupdestpath, os.path.basename(zitem)) + backupFileSuffix
                  # create skeleton directory structure under backupFolder if necessary 
                  if not os.path.exists(backupdestpath): os.makedirs(backupdestpath)
                  shutil.move(tofile, backupfilename)
                  #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upzipFile() move(%s, %s)" % (tofile,backupfilename))
               
               # extract the file
               f = open(tofile, 'wb')
               f.write(z.read(zitem))
               f.close()
   
               # set/update metadata 
               newRevisionNumber = oldRevisionNumber + 1
               setMetadata(tofile, section="GENERAL", option="revision", value=newRevisionNumber)

      #zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upzipFile() finished unzip'ing %s" % FSfilename)
      return 1

   else:
      zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upzipFile() ABORTED: %s not a valid zip file." % FSfilename )
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
      # failure should throw an exception, but for now, return easily identified bogus checksum 
      return "99999999999999999999999999999999"

# --------------------------------------------------------------------
def determine_bytes_usage(startObject):
    """ 
        attempt to determine the total size in bytes of all subobjects of object.
        Note: this only gathers sizes of objects that have the 'get_size' attribute.
    """
    exclude_quota_objects = [] # not used now, but might come in handy at some point
    
    obj_sizes = [ obj.get_size() for id, obj in startObject.ZopeFind( startObject, search_sub=1 ) if hasattr( aq_base( obj ), 'get_size') and getattr( obj, 'meta_type', None ) not in exclude_quota_objects ]
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
        return 'The id is invalid because it contains characters illegal in URLs.'
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

