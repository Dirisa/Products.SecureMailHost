from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.PloneHelpCenter.config import *
from Products.CMFCore.utils import getToolByName
from Products.PloneHelpCenter.Extensions import HCWorkflow, HCFolderWorkflow

from StringIO import StringIO

def registerNavigationTreeSettings(self, out):
    """Make the folderish content types not appear in navigation tree.
    We don't want users to think of the HowTo as a folder, even though
    technically, it is."""

    data = ['HelpCenterHowTo','HelpCenterTutorial','HelpCenterErrorReference', 'HelpCenterFAQ']
    pp=getToolByName(self,'portal_properties')
    p = getattr(pp , 'navtree_properties', None)
    mdntl = list(p.getProperty('metaTypesNotToList', []))
    if not mdntl:
        p._setProperty('metaTypesNotToList', data)
    else:
        for t in data:
            if t not in mdntl:
                mdntl.append(t)
        p._updateProperty('metaTypesNotToList', mdntl)

def install(self):
    out = StringIO()

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)

    #register the folderish items in portal_properties/site_properties
    #appears that Archetypes takes care of this for us.
    #site_props = getToolByName(self, 'portal_properties').site_properties
    #use_folder_tabs = site_props.getProperty('use_folder_tabs', None)
    #if not 'HelpCenterFAQFolder' in use_folder_tabs:
    #    site_props._updateProperty('use_folder_tabs', tuple(use_folder_tabs) + ('HelpCenterFAQFolder',))
    # print >> out, "Added HelpCenterFAQFolder to portal_properties/site_properties/use_folder_tabs"

    registerNavigationTreeSettings(self, out)

    HCWorkflow.install()
    HCFolderWorkflow.install()
    wf_tool = getToolByName(self, 'portal_workflow')

    if not 'helpcenter_workflow' in wf_tool.objectIds():
        wf_tool.manage_addWorkflow('helpcenter_workflow (Workflow for Help Center.)',
                                   'helpcenter_workflow')
    if not 'helpcenterfolder_workflow' in wf_tool.objectIds():
        wf_tool.manage_addWorkflow('helpcenterfolder_workflow (Workflow for Help Center Folders.)',
                                   'helpcenterfolder_workflow')
    wf_tool.updateRoleMappings()

    print >> out, 'Installed helpcenter_workflow.'
    print >> out, 'Installed helpcenterfolder_workflow.'
    
    wf_tool.setChainForPortalTypes(pt_names=['HelpCenterFAQ','HelpCenterHowTo','HelpCenterLink'
                                            ,'HelpCenterTutorial','HelpCenterTutorialPage'
                                            ,'HelpCenterErrorReference','HelpCenterDefinition'], chain='helpcenter_workflow')
    print >> out, 'Set helpcenter_workflow as default for help center content types.'

    wf_tool.setChainForPortalTypes(pt_names=['HelpCenterFAQFolder','HelpCenterHowToFolder',
                                             'HelpCenterLinkFolder','HelpCenterTutorialFolder',
                                             'HelpCenterErrorReferenceFolder',
                                             'HelpCenterGlossary'], chain='helpcenterfolder_workflow')
    print >> out, 'Set helpcenterfolder_workflow as default for help center folder types.'

    fc_tool = getToolByName(self, 'portal_form_controller')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterHowTo', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterFAQ', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterTutorial', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterTutorialPage', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterLink', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterErrorReference', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterDefinition', None, 'traverse_to', 'string:edit_reminder')
    print >> out, 'Set reminder to publish message hack on objects.'

    # make new types use portal_factory
    ft = getToolByName(self, 'portal_factory')    portal_factory_types = ft.getFactoryTypes().keys()    for t in ['HelpCenter'
             ,'HelpCenterGlossary', 'HelpCenterDefinition'
             ,'HelpCenterErrorReference', 'HelpCenterErrorReferenceFolder'
             ,'HelpCenterFAQ', 'HelpCenterFAQFolder'
             ,'HelpCenterHowTo', 'HelpCenterHowToFolder'
             ,'HelpCenterLink', 'HelpCenterLinkFolder'
             ,'HelpCenterTutorial', 'HelpCenterTutorialFolder'
             ,'HelpCenterTutorialPage']:

        if t not in portal_factory_types:            portal_factory_types.append(t)    ft.manage_setPortalFactoryTypes(listOfTypeIds=portal_factory_types)    print >> out, 'New types use portal_factory'

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
