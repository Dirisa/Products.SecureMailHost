import os
import string
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from ConfigParser import ConfigParser
from Acquisition import aq_base

import zLOG

MD5_LENGTH = 32

# Note: the utility methods in this file depend on external system calls.
# These methods have only been tested with the following utilities:
#   * unzip/zipinfo: UnZip v5.50 by Info-ZIP (http://www.info-zip.org/) 
#   * md5: md5deep v1.2 (http://md5deep.sourceforge.net/)
# The following settings are specific to the aforementioned utilities. 

# For now, locally define these system calls and expected return value results.
# (it would be nice if these were properties!)

SYSCALL_ZIPINFO         = "c:\\plone-utils\\unzip -Zt"
SYSCALL_ZIPINFO_SUCCESS = 0

SYSCALL_UNZIP           = "c:\\plone-utils\\unzip -o -d"
SYSCALL_UNZIP_SUCCESS   = 0
SYSCALL_TESTZIP         = "c:\\plone-utils\\unzip -qt"
SYSCALL_TESTZIP_SUCCESS = 0
SYSCALL_GENMD5          = "c:\\plone-utils\\md5deep"
SYSCALL_GENMD5_SUCCESS  = 1

security = ClassSecurityInfo()

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
   try:
      metadataFileParser = ConfigParser()
      metadataFileParser.read(metadataFileName)
      return metadataFileParser.get(section,option)
   except:
      raise 'Metadata Not Found', 'Could not retrieve metadata %s:%s for the file %s.' % (section,option,filename)

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
security.declarePublic('testZipFile')
def testZipFile(filename):
   filename = filename.replace('\\','\\\\')
   syscall = "%s %s" % (SYSCALL_TESTZIP,filename)
   result = os.system(syscall)

   if result == SYSCALL_TESTZIP_SUCCESS:
      return 1
   else:
      zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "testZipFile() FAILED: %s" % syscall )
      return 0 

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'generate_zipinfo')
def generate_zipinfo(filename):

   syscall_filename = filename.replace('\\','\\\\')
   syscall = "%s %s" % (SYSCALL_ZIPINFO,syscall_filename)
   process_fp = os.popen(syscall)
   result = process_fp.read()
   return result

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'setZipInfoMetadata')
def setZipInfoMetadata(filename):

   if testZipFile(filename):
      raw_output = generate_zipinfo(filename)
      files,space = parseZipInfoOutput(raw_output)
   
      setMetadata(filename, section="ZIPINFO", option="num_files", value=files)
      setMetadata(filename, section="ZIPINFO", option="unpacked_size", value=space)
      return 1

   else:
      return 0

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'parseZipInfoOutput')
def parseZipInfoOutput(raw_output):

   FILECOUNT_STARTPOINT = 0
   FILECOUNT_DELIMITER = " files, "
   UNZIPSIZE_DELIMITER = " bytes uncompressed,"
   
   filecount_str = '0'
   unzipsize_str = '0'
   
   if raw_output != None:  
      filecount_endpoint = string.find(raw_output, FILECOUNT_DELIMITER)
      if filecount_endpoint != -1:
         filecount_str = raw_output[FILECOUNT_STARTPOINT:filecount_endpoint]
         
         unzipsize_startpoint = filecount_endpoint + len(FILECOUNT_DELIMITER)
         unzipsize_endpoint = string.find(raw_output,UNZIPSIZE_DELIMITER)
         if unzipsize_endpoint != -1:
            unzipsize_str = raw_output[unzipsize_startpoint:unzipsize_endpoint]

   return filecount_str,unzipsize_str

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'upzipFile') 
def upzipFile(filename):
   if testZipFile(filename):
      filename = filename.replace('\\','\\\\')
      exdir = os.path.dirname(filename)
      syscall = "%s %s %s" % (SYSCALL_UNZIP,exdir,filename)
      result = os.system(syscall)
      if result == SYSCALL_UNZIP_SUCCESS:
         zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upzipFile() SUCCESS: %s" % syscall )
         return 1
      else:
         zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upzipFile() FAILED: %s" % syscall )
         return 0 
   else:
         zLOG.LOG('PloneLocalFolderNG', zLOG.INFO , "upzipFile() ABORTED: %s not a valid zip file." % filename )
         return 0    

# --------------------------------------------------------------------
security.declareProtected(ModifyPortalContent, 'generate_md5')
def generate_md5(filename):
   syscall_filename = filename.replace('\\','\\\\')
   syscall = "%s %s" % (SYSCALL_GENMD5,syscall_filename)
   process_fp = os.popen(syscall)
   md5 = process_fp.read()[:MD5_LENGTH]
   if len(md5) == MD5_LENGTH:
      return md5
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
