import os
from StringIO import StringIO

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.PloneCollectorNG.config import *
from Products.CMFCore.utils import getToolByName


configlets = \
( { 'id'         : 'PloneCollectorNG'
  , 'name'       : 'PloneCollectorNG member preferences'
  , 'action'     : 'string:pcng_member_preferences'
  , 'category'   : 'Member'
  , 'appId'      : 'PloneCollectorNG'
  , 'permission' : 'View'
  , 'imageUrl'   : 'collector_icon.gif'
  }
,
)

def install(self):                                       
    out = StringIO()

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)

    # remove Plone's default workflow from PloneIssueNG
    workflow_tool = getToolByName(self, 'portal_workflow')
    try:
        workflow_tool.setChainForPortalTypes(('PloneIssueNG',), '')    
    except: pass
    print >> out, "Added 'pcng_issue_workflow' workflow"

    # add some new properties to memberdatatool
    memberdata_tool = getToolByName(self, 'portal_memberdata')

    for key,default, tpe  in (
               ('pcng_company', '', 'string') , 
               ('pcng_position', '', 'string') , 
               ('pcng_city', '', 'string') , 
               ('pcng_substitute', [] , 'lines'),
               ('pcng_address', '', 'string') , 
               ('pcng_fax', '', 'string') , 
               ('pcng_email_submission_permission','no', 'string'),
               ('pcng_send_emails','yes', 'string'),
               ('pcng_send_attachments','no', 'string'),
               ('pcng_position_searchform','bottom', 'string'),
               ('pcng_default_searchform','simple', 'string'),
               ('pcng_hits_per_page', 15 , 'int'),
               ('pcng_issue_in_new_window', 0 , 'int'),
               ('pcng_saved_searches', [] , 'lines'),
               ('pcng_default_view', 'simple', 'string'),
               ('pcng_phone', '', 'string') ):
        try:
            memberdata_tool.manage_addProperty(key, default, tpe)
            print >>out, 'Added "%s" to memberdata_tool' % key
        except: 
            print >>out, 'Skipping "%s" - already in memberdata_tool' % key

    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            print >>out, 'Adding configlet %s\n' % conf['id']
            configTool.registerConfiglet(**conf)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()


def uninstall(self):                                       
    out = StringIO()

    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            print >>out, 'Removing configlet %s\n' % conf['id']
            configTool.unregisterConfiglet(conf['id'])

    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
