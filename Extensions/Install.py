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

    data = ['HelpCenterHowTo','HelpCenterTutorial','HelpCenterErrorReference',
            'HelpCenterFAQ', 'HelpCenterDefinition', 'HelpCenterLink'
            'HelpCenterInstructionalVideo', 'HelpCenterReferenceManual']
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

def install_portlets(self, out):
    # prepend to the left_slots list, so it appears on top for Reviewers
    self.left_slots = [ 'here/portlet_stale_items/macros/portlet',] + list(self.left_slots)
    print >>out, "Added portlet"

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

    wf_tool.setChainForPortalTypes(pt_names=['HelpCenterFAQ'
                                            ,'HelpCenterHowTo'
                                            ,'HelpCenterLink'
                                            ,'HelpCenterTutorial'
                                            ,'HelpCenterReferenceManual'
                                            ,'HelpCenterInstructionalVideo'
                                            ,'HelpCenterErrorReference'
                                            ,'HelpCenterDefinition'], chain='helpcenter_workflow')
    print >> out, 'Set helpcenter_workflow as default for help center content types.'

    wf_tool.setChainForPortalTypes(pt_names=['HelpCenterFAQFolder'
                                            ,'HelpCenterHowToFolder'
                                            ,'HelpCenterLinkFolder'
                                            ,'HelpCenterTutorialFolder'
                                            ,'HelpCenterReferenceManualFolder'
                                            ,'HelpCenterInstructionalVideoFolder'
                                            ,'HelpCenterErrorReferenceFolder'
                                            ,'HelpCenterGlossary'], chain='helpcenterfolder_workflow')
    print >> out, 'Set helpcenterfolder_workflow as default for help center folder types.'

    # Remove workflow from Tutorial Pages, code from ZWiki, can probably be simpler ~limi
    cbt = wf_tool._chains_by_type
    if cbt is None:
        cbt = PersistentMapping()
    cbt['HelpCenterTutorialPage'] = []
    wf_tool._chains_by_type = cbt
    print >> out, 'Set no workflow as default for Help Center TutorialPages.'

    fc_tool = getToolByName(self, 'portal_form_controller')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterHowTo', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterFAQ', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterTutorial', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterReferenceManual', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterInstructionalVideo', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterLink', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterErrorReference', None, 'traverse_to', 'string:edit_reminder')
    fc_tool.addFormAction('content_edit', 'success', 'HelpCenterDefinition', None, 'traverse_to', 'string:edit_reminder')
    print >> out, 'Set reminder to publish message hack on objects.'

    # make new types use portal_factory
    ft = getToolByName(self, 'portal_factory')
    portal_factory_types = ft.getFactoryTypes().keys()
    for t in ['HelpCenter'
             ,'HelpCenterGlossary'
             ,'HelpCenterDefinition'
             ,'HelpCenterErrorReference'
             ,'HelpCenterErrorReferenceFolder'
             ,'HelpCenterFAQ'
             ,'HelpCenterFAQFolder'
             ,'HelpCenterHowTo'
             ,'HelpCenterHowToFolder'
             ,'HelpCenterInstructionalVideo'
             ,'HelpCenterInstructionalVideoFolder'
             ,'HelpCenterLink'
             ,'HelpCenterLinkFolder'
             ,'HelpCenterTutorial'
             ,'HelpCenterTutorialFolder'
             ,'HelpCenterTutorialPage'
             ,'HelpCenterReferenceManual'
             ,'HelpCenterReferenceManualFolder'
             ,'HelpCenterReferenceManualSection'
             ,'HelpCenterReferenceManualPage']:

        #if t not in portal_factory_types:
        #    portal_factory_types.append(t)
        #    ft.manage_setPortalFactoryTypes(listOfTypeIds=portal_factory_types)

        # XXX: Until the bug in Portal Factory that causes insufficient privileges
        # is fixed in a stable release of Plone, we CANNOT use portal_factory for
        # our types, given that we use the "Add portal content" permission in
        # individual folder to allow people to add things.

        # Either that bug needs to be fixed, or we need to rewrite our FTIs to use
        # different permissions for adding the folders versus the user-addable
        # content (which is probably a VERY good thing for someone to do).

        # But don't uncomment those lines above until someone does one of those two
        # things. - joel@joelburton.com

        pass

    print >> out, 'New types use portal_factory'

    # Add "stale items" portlet, so HelpCenter Managers and Reviewers can
    # review old stuff to see if it's still useful
    install_portlets(self, out)
    
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall(self):
    out = StringIO()

    # remove the stale-items portlet from the portal root object
    portletPath = 'here/portlet_stale_items/macros/portlet'
    if portletPath in self.left_slots:
        self.left_slots = [p for p in self.left_slots if (p != portletPath)]
        print >> out, 'Removed stale-items portlet'

    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
