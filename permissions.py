from Products.CMFCore.CMFCorePermissions import setDefaultRoles

SendForm = 'Send PloneFormMailer Form'
setDefaultRoles(SendForm, ('Manager', 'Owner', 'Member'))
