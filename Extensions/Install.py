import os
from StringIO import StringIO

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.PloneCollectorNG.config import *
from Products.CMFCore.utils import getToolByName

def install(self):                                       
    out = StringIO()

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)

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

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
