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
                                                                                                        
    filename = 'pcng_issue_workflow.zexp'
    src_path = self.getPhysicalRoot().Control_Panel.Products.PloneCollectorNG.home
    import_dir = os.path.join(INSTANCE_HOME, 'import')
    src_file =  open(os.path.join(src_path, 'import', filename), 'rb')
    if not os.path.exists(import_dir): os.makedirs(import_dir)
    dest_file = open(os.path.join(import_dir, filename), 'wb')
    dest_file.write(src_file.read())
    src_file.close(); dest_file.close()

    workflow_tool = getToolByName(self, 'portal_workflow')
    workflow_tool.manage_importObject(filename)

    os.unlink(os.path.join(import_dir, filename))
    workflow_tool.setChainForPortalTypes(('PloneIssueNG',), 'pcng_issue_workflow')    
    print >> out, "Added 'pcng_issue_workflow' workflow"


    # add some new properties to memberdatatool
    memberdata_tool = getToolByName(self, 'portal_memberdata')

    for key,default, tpe  in (
               ('pcng_company', '', 'string') , ('pcng_position', '', 'string') , 
               ('pcng_city', '', 'string') , ('pcng_substitute', [] , 'lines'),
               ('pcng_address', '', 'string') , ('pcng_fax', '', 'string') , 
               ('pcng_send_attachments','no', 'string'),
               ('pcng_phone', '', 'string') ):
        try:
            memberdata_tool.manage_addProperty(key, default, tpe)
            print >>out, 'Added "%s" to memberdata_tool' % key
        except: 
            print >>out, 'Skipping "%s" - already in memberdata_tool' % keys

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
