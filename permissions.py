"""
$Id: permissions.py,v 1.2 2005/03/11 11:59:14 optilude Exp $
"""
from Products.CMFCore.CMFCorePermissions import setDefaultRoles

ADD_CONTENT_PERMISSION = 'Add PloneSoftwareCenter Content'

# Let members add new packages for review
setDefaultRoles(ADD_CONTENT_PERMISSION, ('Member', 'Manager','Owner',))