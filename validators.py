from Products.validation.interfaces import ivalidator
import os, os.path

class ExistingFolderValidator:
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
        