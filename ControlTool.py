"""
$Id: ControlTool.py,v 1.11 2004/12/15 21:01:46 rafrombrc Exp $
"""
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, DevelopmentMode
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.Archetypes.utils import findDict
from Products.Archetypes.public import *
from Products.Archetypes.Schema import FieldList
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.portal_memberdata import MemberData \
     as IMemberData

from Products.CMFMember.Extensions.Workflow import setupWorkflow
from Products.CMFMember.MemberDataContainer import getMemberFactory
import Products.CMFMember as CMFMember

import zLOG
import traceback
import sys
import types

def log(message,summary='',severity=0):
    zLOG.LOG('CMFMember: ', severity, summary, message)

def modify_fti(fti, allowed = ()):
    fti['filter_content_types'] = 1
    fti['allowed_content_types'] = ''
    refs = findDict(fti['actions'], 'id', 'references')
    refs['visible'] = 0
    refs = findDict(fti['actions'], 'id', 'view')
    refs['name'] = 'Overview'
    refs['action'] = 'string:prefs_cmfmember_migration_overview'
    refs = findDict(fti['actions'], 'id', 'edit')
    refs['visible'] = 0
    refs = findDict(fti['actions'], 'id', 'metadata')
    refs['visible'] = 0

    
_upgradePaths = {}
_memberPaths = {}
_widgetRegistry = {}
control_id = 'cmfmember_control'
configlets = [ {'id':'cmfmember',
     'appId':'CMFMember',
     'name':'CMFMember control',
     'action':'string:${portal_url}/' + control_id + '/prefs_cmfmember_migration',
     'category':'Products',
     'permission': ManagePortal,
     'imageUrl':'group.gif'},]



# groups for our setup configlets
group = 'cmfmember|CMFMember|CMFMember setup'

class ControlTool( UniqueObject, BaseBTreeFolder):
    """Handles migrations between CMFMember releases"""

    id = control_id
    archetype_name = portal_type = meta_type = 'ControlTool'

    _needRecatalog = 0
    _needUpdateRole = 0

    global_allow = 0
    use_folder_tabs = 0
    
    # Used to set the default type in MemberDataContainer and migrations
    default_member_type = 'Member'
    
    actions = (
        { 'id'            : 'migrations',
          'name'          : 'Migrations',
          'action'        : 'string:prefs_cmfmember_migration',
          'permissions'   : (CMFCorePermissions.ManageProperties,),
          'category'      : 'object',
        },
        { 'id'            : 'setup',
          'name'          : 'Setups',
          'action'        : 'string:prefs_cmfmember_setup',
          'permissions'   : (CMFCorePermissions.ManageProperties,),
          'category'      : 'object',
        },)

    manage_options = (
        { 'label' : 'Overview', 'action' : 'manage_overview' },
        { 'label' : 'Migrate', 'action' : 'manage_migrate' },
        { 'label' : 'Import', 'action' : 'manage_import' },
        { 'label' : 'Setup', 'action' : 'manage_setup' }, ) + ActionProviderBase.manage_options


    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_overview')
    security.declareProtected(ManagePortal, 'manage_migrate')
    security.declareProtected(ManagePortal, 'manage_import')

    import os
    _www = os.path.join(os.path.dirname(__file__), 'www')

    manage_import = PageTemplateFile('import.pt', _www)
    manage_migrate = PageTemplateFile('migration.pt',_www)
    manage_overview = PageTemplateFile('migration_overview.pt', _www)
    manage_setup = PageTemplateFile('setup.pt', _www)

    version = ''
    
    def __init__(self, oid = None):
        if not oid: oid = self.id
        BaseBTreeFolder.__init__(self, oid)
        
    # Add a visual note
    def om_icons(self):
        icons = ({
                    'path':'misc_/CMFMember/cmfmember_control_icon.png',
                    'alt':self.meta_type,
                    'title':self.meta_type,
                 },)
        if self.needUpgrading() \
           or self.needUpdateRole() \
           or self.needRecatalog():
            icons = icons + ({
                     'path':'misc_/PageTemplates/exclamation.gif',
                     'alt':'Error',
                     'title':'This Plone instance needs updating'
                  },)

        return icons

    ##############################################################
    # Public methods
    #
    # versions methods

    
    security.declareProtected(ManagePortal, 'getLog')
    def getLog(self):
        return getattr(self, '_log', None) 
    
    security.declareProtected(ManagePortal, 'getInstanceVersion')
    def getInstanceVersion(self):
        """ The version of installed CMFMember """
        # when we support more then one memberdata folder this check may 
        # have to be changed since different memberdata folders could be
        # different versions but shouldn't :)
        if getattr(self, 'version', '') == '':
            memberdata_tool = self.portal_memberdata
            if hasattr(memberdata_tool.__class__, 'portal_type') \
               and (memberdata_tool.__class__.portal_type == 'CMFMember Tool' \
               or memberdata_tool.__class__.portal_type == 'MemberDataContainer'):
                if hasattr(self.portal_memberdata,'getVersion'):
                    self.version = self.portal_memberdata.getVersion()
                else:
                    self.version = 'development'
            else:
                self.version = 'plone'
        return self.version.lower()

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def setInstanceVersion(self, version):
        """ The version this instance of Plone is on """
        self.version = version

    security.declareProtected(ManagePortal, 'knownVersions')
    def knownVersions(self):
        """ All known version IDs, except current one """
        return _upgradePaths.keys()

    def knowMemberMigrations(self):
        """ All known member migrations """
        return _memberPaths
    
    security.declareProtected(ManagePortal, 'getDefaultMemberType')
    def getDefaultMemberType(self):
        """ Return default member type set in the migration form or from the MemberDataContainer. """
        return self.default_member_type
        
    security.declareProtected(ManagePortal, 'getAvailableMemberTypes')
    def getAvailableMemberTypes(self):
        """ Return available member types. Used in migration. """
        at_tool = getToolByName(self, 'archetype_tool')
        return [ klass.portal_type for klass in at_tool.listTypes()\
                 if IMemberData.isImplementedByInstancesOf(klass) ]

    security.declareProtected(ManagePortal, 'getCurrentMemberWorkflow')
    def getCurrentMemberWorkflow(self):
        """ Return the workflow associated with the current default member type."""
        def_mem_type = self.getDefaultMemberType()
        chain = getToolByName(self, 'portal_workflow').getChainFor(def_mem_type)
        if chain:
            return chain[0]
        else:
            return ''

    security.declareProtected(ManagePortal, 'getAvailableWorkflows')
    def getAvailableMemberWorkflows(self):
        """ Return available workflows. Used to define default workflow. """
        return getToolByName(self, 'portal_workflow').objectIds()

    security.declareProtected(ManagePortal, 'getFileSystemVersion')
    def getFileSystemVersion(self):
        """ The version this instance of Plone is on """
        return self.Control_Panel.Products.CMFMember.version.lower()

    security.declareProtected(ManagePortal, 'getMemberTypesFileSystemVersion')
    def getMemberTypesFileSystemVersion(self):
        """ The version this instance of Plone is on """
        portal = getToolByName(self, 'portal_url')
        memberdata_tool = portal.portal_memberdata
        vars = {}
        tempFolder = PortalFolder('temp').__of__(self)
        # don't store tempFolder in the catalog
        tempFolder.unindexObject()

        # get information form old MemberDataTool
        if hasattr(memberdata_tool.__class__, 'portal_type') \
           and memberdata_tool.__class__.portal_type == 'CMFMember Tool':
            member_type = memberdata_tool.typeName
            getMemberFactory(tempFolder, member_type)(member_type)
            memberInstance = getattr(tempFolder,member_type)
            getattr(tempFolder,member_type).unindexObject()
            # don't store memberInstance in the catalog
            vars[member_type] = memberInstance.version.lower()
            memberInstance.unindexObject()
        elif memberdata_tool.__class__ == CMFMember.MemberDataContainer.MemberDataContainer:
            for member_type in memberdata_tool.getAllowedMemberTypes():
                getMemberFactory(tempFolder, member_type)(member_type)
                memberInstance = getattr(tempFolder,member_type)
                getattr(tempFolder,member_type).unindexObject()
                # don't store memberInstance in the catalog
                vars[member_type] = memberInstance.version.lower()
                memberInstance.unindexObject() 
        return vars.items()
    
    security.declareProtected(ManagePortal, 'needUpgrading')
    def needUpgrading(self):
        """ Need upgrading? """
        need = self.getInstanceVersion() != self.getFileSystemVersion()
        if need:
            self.setTitle('CMFMember not up to date')
        else:
            self.setTitle('CMFMember up to date')
        return need



    security.declareProtected(ManagePortal, 'coreVersions')
    def coreVersions(self):
        """ Useful core information """
        vars = {}
        cp = self.Control_Panel
        vars['CMFMember Instance'] = self.getInstanceVersion()
        vars['CMFMember File System'] = self.getFileSystemVersion()
            
        return vars

    security.declareProtected(ManagePortal, 'coreVersionsList')
    def coreVersionsList(self):
        """ Useful core information """
        res = self.coreVersions().items()
        res.sort()
        return res

    security.declareProtected(ManagePortal, 'needUpdateRole')
    def needUpdateRole(self):
        """ Do roles need to be updated? """
        return self._needUpdateRole

    security.declareProtected(ManagePortal, 'needRecatalog')
    def needRecatalog(self):
        """ Does this thing now need recataloging? """
        return self._needRecatalog

    ##############################################################
    # the setup widget registry
    # this is a whole bunch of wrappers
    # Really an unprotected sub object
    # declaration could do this...

    def _getWidget(self, widget):
        """ We cant instantiate widgets at run time
        but can send all get calls through here... """
        _widget = _widgetRegistry[widget]
        obj = getToolByName(self, 'portal_url').getPortalObject()
        return _widget(obj)

    security.declareProtected(ManagePortal, 'listWidgets')
    def listWidgets(self):
        """ List all the widgets """
        return _widgetRegistry.keys()

    security.declareProtected(ManagePortal, 'getDescription')
    def getDescription(self, widget):
        """ List all the widgets """
        return self._getWidget(widget).description

    security.declareProtected(ManagePortal, 'listAvailable')
    def listAvailable(self, widget):
        """  List all the Available things """
        return self._getWidget(widget).available()

    security.declareProtected(ManagePortal, 'listInstalled')
    def listInstalled(self, widget):
        """  List all the installed things """
        return self._getWidget(widget).installed()

    security.declareProtected(ManagePortal, 'listNotInstalled')
    def listNotInstalled(self, widget):
        """ List all the not installed things """
        avail = self.listAvailable(widget)
        install = self.listInstalled(widget)
        return [ item for item in avail if item not in install ]

    security.declareProtected(ManagePortal, 'activeWidget')
    def activeWidget(self, widget):
        """ Show the state """
        return self._getWidget(widget).active()

    security.declareProtected(ManagePortal, 'setupWidget')
    def setupWidget(self, widget):
        """ Show the state """
        return self._getWidget(widget).setup()

    security.declareProtected(ManagePortal, 'runWidget')
    def runWidget(self, widget, item, **kwargs):
        """ Run the widget """
        return self._getWidget(widget).run(item, **kwargs)

    security.declareProtected(ManagePortal, 'installItems')
    def installItems(self, widget, items):
        """ Install the items """
        return self._getWidget(widget).addItems(items)

    ##############################################################

    security.declareProtected(ManagePortal, 'upgrade')
    def upgrade(self, REQUEST=None, dry_run=None, swallow_errors=1, default_member_type='Member', default_workflow=None, upgrade_workflows=False):
        """ perform the upgrade """
        
        # keep it simple
        out = []
        
        # reinstall CMFMember default workflows
        if upgrade_workflows:
            setupWorkflow(getToolByName(self, 'portal_url'), out, force_reinstall=True)
            out.append(('Workflows reinstalled', zLOG.INFO))

        self.default_member_type = default_member_type
        
        # Set the default workflow for the selected default member type
        if default_workflow:
            wf_tool = getToolByName(self, 'portal_workflow')
            wf_tool.setChainForPortalTypes((default_member_type,), default_workflow)
            wf_tool.updateRoleMappings()
            out.append(('Workflow for %s  set to %s' % (default_member_type, default_workflow), zLOG.INFO))
            
        self._check()
        failed = 0
        if dry_run:
            out.append(("Dry run selected.", zLOG.INFO))

        if REQUEST is not None:
            newv = REQUEST.get('force_instance_version', self.getInstanceVersion())
        else:
            newv = self.getInstanceVersion()

        out.append(("Starting the migration from "
                    "version: %s" % newv, zLOG.INFO))

        # reinstall the CMFMember product, if necessary
        qi_tool = getToolByName(self, 'portal_quickinstaller')
        inst_vers = [prod['installedVersion'] \
                     for prod in qi_tool.listInstalledProducts() \
                     if prod['id'] == 'CMFMember']
        fs_vers = qi_tool.getProductVersion('CMFMember')
    
        if len(inst_vers) and inst_vers[0] != fs_vers:
            out.append(('Reinstalling CMFMember Product', zLOG.INFO))
            qi_tool.reinstallProducts(['CMFMember'])

        while newv is not None:
            out.append(("Attempting to upgrade from: %s" % newv, zLOG.INFO))
            # commit work in progress between each version
            #get_transaction().commit(1)
            # if we modify the portal root and commit a sub transaction
            # the skin data will disappear, explicitly set it up on each
            # subtrans, the alternative is to traverse again to the root on
            # after each which will trigger the normal implicit skin setup.
            aq_parent( aq_inner( self ) ).setupCurrentSkin()
            try:
                newv, msgs = self._upgrade(newv)
                if msgs:
                    for msg in msgs:
                        # if string make list
                        if type(msg) == type(''):
                            msg = [msg,]
                        # if no status, add one
                        if len(msg) == 1:
                            msg.append(zLOG.INFO)
                        out.append(msg)
                if newv is not None:
                    out.append(("Upgrade to: %s, completed" % newv, zLOG.INFO))
                    self.setInstanceVersion(newv)

            except:
                out.append(("Upgrade aborted", zLOG.ERROR))
                out.append(("Error type: %s" % sys.exc_type, zLOG.ERROR))
                out.append(("Error value: %s" % sys.exc_value, zLOG.ERROR))
                for line in traceback.format_tb(sys.exc_traceback):
                    out.append((line, zLOG.ERROR))

                # set newv to None
                # to break the loop
                newv = None
                failed = 1
                if swallow_errors:
                    # abort transaction to safe the zodb
                    get_transaction().abort()
                else:
                    for msg, sev in out: log(msg, severity=sev)
                    raise

        out.append(("End of upgrade path, migration has finished", zLOG.INFO))

        if self.needUpgrading():
            out.append((("The upgrade path did NOT reach "
                        "current version"), zLOG.PROBLEM))
            out.append(("Migration has failed", zLOG.PROBLEM))
        else:
            out.append((("Your ZODB and Filesystem Plone "
                         "instances are now up-to-date."), zLOG.INFO))

        # do this once all the changes have been done
        if not failed and self.needRecatalog():
            try:
                self.portal_catalog.refreshCatalog()
                self._needRecatalog = 0
            except:
                out.append(("Exception was thrown while cataloging",
                            zLOG.ERROR))
                out += traceback.format_tb(sys.exc_traceback)
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise

        if not failed and self.needUpdateRole():
            try:
                self.portal_workflow.updateRoleMappings()
                self._needUpdateRole = 0
            except:
                out.append((("Exception was thrown while updating "
                             "role mappings"), zLOG.ERROR))
                out += traceback.format_tb(sys.exc_traceback)
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise
                    
        
        if dry_run:
            out.append(("Dry run selected, transaction aborted", zLOG.INFO))
            # abort all work done in this transaction, this roles back work
            # done in previous sub transactions
            get_transaction().abort()

        # log all this to the ZLOG
        for msg, sev in out:
            log(msg, severity=sev)

        self._log = out

        if REQUEST:
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/prefs_cmfmember_migration')
        
    def getConfiglets(self):
        return tuple(configlets)
    ##############################################################
    # Private methods

    def _check(self):
        """ Are we inside a Plone site?  Are we allowed? """
        if not hasattr(self,'portal_url'):
            raise 'You must be in a Plone site to migrate.'

    def _upgrade(self, version):
        version = version.lower().strip()
        if not _upgradePaths.has_key(version):
            return None, ("No upgrade path found from %s" % version,)

        newversion, function = _upgradePaths[version]
        res = function(self.aq_parent)
        return newversion, res

def registerUpgradePath(oldversion, newversion, function, type = 'Standard'):
    """ Basic register func """
    if type != 'Member':
        _upgradePaths[oldversion.lower()] = [newversion.lower(), function]
    else:
        _memberPaths[oldversion.lower()] = [newversion.lower(), function]

def registerSetupWidget(widget):
    """ Basic register things """
    for wc in widget.configlets:
        configlets.append(wc)
    _widgetRegistry[widget.type] = widget

registerType(ControlTool, 'CMFMember')
InitializeClass(ControlTool)
