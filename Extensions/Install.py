from Products.PloneSoftwareCenter.config import *
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

folderish = ('PSCProject', 'PSCRelease', 'PloneSoftwareCenter')

# Get the custom workflows
from Products.PloneSoftwareCenter.Extensions import AreaWorkflow
from Products.PloneSoftwareCenter.Extensions import ImprovementProposalWorkflow
from Products.PloneSoftwareCenter.Extensions import PackageWorkflow
from Products.PloneSoftwareCenter.Extensions import ReleaseWorkflow


def setWorkflowForType (self, out, tool, type, workflowName):
    """Set the workflow for a given type"""
    
    tool.setChainForPortalTypes ((type,), workflowName)
    
    print >> out, "Set workflow for %s to %s" % (type, workflowName,)
     
def addWorkflow (self, out, tool, workflowName, workflowId):
    """Add the givne workflow. The workflowName must be the exact name set
    in the workflow, which in turn must have been registered with the
    workflows factory.
    """
    
    if not workflowId in tool.objectIds ():
        tool.manage_addWorkflow(workflowName, workflowId)
        print >> out, "Added workflow", workflowName 


def installWorkflows (self, out):

    workflow = getToolByName (self, 'portal_workflow')

    print >> out, "Installing custom workflows"
    
    # Register the workflows
    
    AreaWorkflow.install ()
    ImprovementProposalWorkflow.install ()
    PackageWorkflow.install ()
    ReleaseWorkflow.install ()
    
    addWorkflow (self, out, workflow,   
                    'psc_area_workflow (PSC Area workflow)',
                    'psc_area_workflow')
    addWorkflow (self, out, workflow,   
                    'psc_improvementproposal_workflow (PSC Improvement Proposal workflow)',
                    'psc_improvementproposal_workflow')
    addWorkflow (self, out, workflow,   
                    'psc_package_workflow (PSC Package workflow)',
                    'psc_package_workflow')
    addWorkflow (self, out, workflow,   
                    'psc_release_workflow (PSC Release workflow)',
                    'psc_release_workflow')    
    
    workflow.updateRoleMappings ()    
    
    # Enable the workflow for the types
    setWorkflowForType (self, out, workflow, 
                            'PSCProject', 
                            'psc_package_workflow')
    setWorkflowForType (self, out, workflow, 
                            'PloneSoftwareCenter', 
                            'psc_area_workflow')
    setWorkflowForType (self, out, workflow, 
                            'PSCFile', 
                            '')
    setWorkflowForType (self, out, workflow, 
                            'PSCImprovementProposal', 
                            'psc_improvementproposal_workflow')
    setWorkflowForType (self, out, workflow, 
                            'PSCImprovementProposalFolder', 
                            '') 
    setWorkflowForType (self, out, workflow, 
                            'PSCRelease', 
                            'psc_release_workflow')
    setWorkflowForType (self, out, workflow, 
                            'PSCReleaseFolder',  
                            '')    
    
    workflow.updateRoleMappings ()
     
    
    print >> out, "Done installing workflows"
    

def satisfyDependencies(self, out):
    qi = getToolByName(self, 'portal_quickinstaller')
    def install(product, hard):
        if product not in qi.objectIds():
            try: # try to install
                qi.installProduct(dep)
            except AttributeError: # qi raised, bail out if hard dep
                msg = "Failed to install %s." % dep
                if hard:
                    raise ValueError, msg
                else:
                    print >> out, msg
            else:
                print >> out, "Installed dependency %s." % dep
        
    for dep in HARD_DEPS:
        install(dep, hard=True)
    for dep in SOFT_DEPS:
        install(dep, hard=False)

def install(self):
    out = StringIO()

    satisfyDependencies(self, out)

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)
    
    installWorkflows(self, out)

    # register folderish types
    pp = getToolByName(self, 'portal_properties')
    use_tabs = tuple(pp.site_properties.use_folder_tabs)
    pp.site_properties._updateProperty('use_folder_tabs', \
                                       use_tabs + folderish)

    print >> out, 'Registered %s as folderish objects' % ",".join(folderish)
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
