from Products.validation.interfaces import ivalidator
import os, os.path
import md5
from util import *
from App.FindHomes import SOFTWARE_HOME

class ExternalMD5UtilityValidator:
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):

        #if not os.path.exists(os.path.normpath(value)):
        #    return """utility not found at specified path"""
        
        if value == 'none':
            return 1
        
        filename = os.path.join(SOFTWARE_HOME,'Products')
        filename = os.path.join(filename,'PloneLocalFolderNG')
        filename = os.path.join(filename,'VERSION.txt')
        
        internalMD5 = generate_md5(filename, 'none')
        externalMD5 = generate_md5(filename, value)
        if internalMD5 != externalMD5:
            if not os.path.exists(os.path.normpath(value)):
                return """utility not found at specified path"""    
            else:
                return """ERROR: the specified external utility does not produce a valid MD5 checksum"""

        return 1
                
class ExistingFolderPathValidator:
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):

        if not value.endswith(os.path.sep):
            return """Invalid path: trailing slash required"""

        if not os.path.isabs(value):
            return """Invalid path: relative path not allowed"""  

        trimmedPath = value[0:len(value)-1]
        if trimmedPath != os.path.normpath(trimmedPath):
            return """Invalid path: path must be normalized"""  

        if not os.path.exists(value):
            return """Folder not found"""
        
        return 1

