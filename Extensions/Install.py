from Products.CMFCore.utils import getToolByName,manage_addTool
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.ExternalMethod.ExternalMethod import ExternalMethod


from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes import listTypes
from Products.PloneSecurityInjector import PROJECTNAME,product_globals

from StringIO import StringIO
import sys

class PloneSkinRegistrar:
    """
    Controls (un)registering of a layer in the skins tool:
     - the layer in the content of the skin tool
     - the layer in the path of all skins
    @author: U{Gilles Lenfant <glenfant@bigfoot.com>}
    @version: 0.1.0
    @ivar _layer: Name of the Product's sudirectory that contains
        the various layers for the Product.
    @type _layer: string
    @ivar _prodglobals: Globals from this Product.
    @type _propglobals: mapping object
    """

    def __init__(self, skinsdir, prodglobals):
        """Constructor
        @param skinsdir: Name of the Product's subdirectory that
            contains the various layers for the Product.
        @type skinsdir: string
        @param prodglobals: Globals from this Product.

            should be provided by Product's C{__init__.py} like this:

            C{product_globals = globals()}

        @type propglobals: mapping object
        @return: None
        """

        self._skinsdir = skinsdir
        self._prodglobals = prodglobals
        return

    def install(self, aq_obj,position=None,mode='after',layerName=None):
        """Installs and registers the skin resources
        @param aq_obj: object from which cmf site object is acquired
        @type aq_obj: any Zope object in the CMF
        @return: Installation log
        @rtype: string
        """

        rpt = '=> Installing and registering layers from directory %s\n' % self._skinsdir
        skinstool = getToolByName(aq_obj, 'portal_skins')

        # Create the layer in portal_skins

        try:
            if self._skinsdir not in skinstool.objectIds():
                addDirectoryViews(skinstool, self._skinsdir, self._prodglobals)
                rpt += 'Added "%s" directory view to portal_skins\n' % self._skinsdir
            else:
                rpt += 'Warning: directory view "%s" already added to portal_skins\n' % self._skinsdir
        except:
            # ugh, but i am in stress
            rpt += 'Warning: directory view "%s" already added to portal_skins\n' % self._skinsdir


        # Insert the layer in all skins
        # XXX FIXME: Actually assumes only one layer directory with the name of the Product
        # (should be replaced by a smarter solution that finds individual Product's layers)

        if not layerName:
            layerName = self._prodglobals['__name__'].split('.')[-1]

        skins = skinstool.getSkinSelections()

        for skin in skins:
            layers = skinstool.getSkinPath(skin)
            layers = [layer.strip() for layer in layers.split(',')]
            if layerName not in layers:
                try:
                    pos=layers.index(position)
                    if mode=='after': pos=pos+1
                except ValueError:
                    pos=len(layers)

                layers.insert(pos, layerName)

                layers = ','.join(layers)
                skinstool.addSkinSelection(skin, layers)
                rpt += 'Added "%s" to "%s" skin\n' % (layerName, skin)
            else:
                rpt += '! Warning: skipping "%s" skin, "%s" is already set up\n' % (skin, type)
        return rpt

    def uninstall(self, aq_obj):
        """Uninstalls and unregisters the skin resources
        @param aq_obj: object from which cmf site object is acquired
        @type aq_obj: any Zope object in the CMF
        @return: Uninstallation log
        @rtype: string
        """

        rpt = '=> Uninstalling and unregistering %s layer\n' % self._skinsdir
        skinstool = getToolByName(aq_obj, 'portal_skins')

        # Removing layer from portal_skins
        # XXX FIXME: Actually assumes only one layer directory with the name of the Product
        # (should be replaced by a smarter solution that finds individual Product's layers)

        if not layerName:
            layerName = self._prodglobals['__name__'].split('.')[-1]

        if layerName in skinstool.objectIds():
            skinstool.manage_delObjects([layerName])
            rpt += 'Removed "%s" directory view from portal_skins\n' % layerName
        else:
            rpt += '! Warning: directory view "%s" already removed from portal_skins\n' % layerName

        # Removing from skins selection

        skins = skinstool.getSkinSelections()
        for skin in skins:
            layers = skinstool.getSkinPath(skin)
            layers = [layer.strip() for layer in layers.split(',')]
            if layerName in layers:
                layers.remove(layerName)
                layers = ','.join(layers)
                skinstool.addSkinSelection(skin, layers)
                rpt += 'Removed "%s" to "%s" skin\n' % (layerName, skin)
            else:
                rpt += 'Skipping "%s" skin, "%s" is already removed\n' % (skin, layerName)
        return rpt
# /class PloneSkinRegistrar

def install_index(self,out):
    print >> out, "Install catalog indizes."

    ctool = getToolByName(self, 'portal_catalog')
    try:
        ctool.manage_addProduct['PluginIndexes'].manage_addFieldIndex(id='review_acquisition_state')
    except:
        print >>out, "Index already category exists"

def install_actions(self,out):
    print >> out, "Install action."    

    self.portal_actions.addAction(name='Acquisition',
                                     id='acquisition',
                                     action='string:${object_url}/acquisition_status_history',
                                     condition='python:"securityinjector_workflow" in portal.portal_securityinjector.getWorkflowFor(object)',
                                     permission='Manage portal',
                                     category='object_tabs',visible=1)
    
    print >>out, "Action was sucessfully installed"

def install_controlpanel_action(self,out):
    print >> out, "Install controlpanel action."

    self.portal_controlpanel.addAction(name='Overview Breakpoints',
                                       id='overview_breakpoints',
                                       action='string:${portal_url}/prefs_breakpoints_view',
                                       condition='',
                                       permission='Manage portal',
                                       category='Plone',
                                       visible=1,
                                       appId='PloneSecurityInjector')
    
    print >> out, "Controlpanel action sucessfully installed"
    print >> out, "Install Action icon."
    
    self.portal_actionicons.addActionIcon(category='controlpanel',
                                          action_id='overview_breakpoints',
                                          icon_expr='mail_icon.gif',
                                          title='Aquisition Overview',
                                          priority=0)

    print >> out, "Action icon sucessfully installed"

def install(self):
    portal=getToolByName(self,'portal_url').getPortalObject()
    out = StringIO()

    print >> out, "Successfully installed %s." % PROJECTNAME
    sr = PloneSkinRegistrar('skins', product_globals)
    print >> out,sr.install(self)

    install_index(self,out)
    install_actions(self,out)
    install_controlpanel_action(self,out)
    
    #autoinstall tools
    for t in ['PloneSecurityInjector']:
        try:
            portal.manage_addProduct[PROJECTNAME].manage_addTool(t)
            # tools are not content. dont list it in navtree
        except:
            #heuristics for testing if an instance with the same name already exists
            #only this error will be swallowed.
            #Zope raises in an unelegant manner a 'Bad Request' error
            e=sys.exc_info()
            if e[0] != 'Bad Request':
                raise

    #hide tools in the navigation
    for t in ['PloneSecurityInjector']:
        try:
            if t not in self.portal_properties.navtree_properties.metaTypesNotToList:
                self.portal_properties.navtree_properties.metaTypesNotToList= \
                   list(self.portal_properties.navtree_properties.metaTypesNotToList) + \
                      [t]
        except TypeError, e:
            print 'Attention: could not set the navtree properties:',e

    #try to call a custom install method
    #in 'AppInstall.py' method 'install'
    try:
        install = ExternalMethod('temp','temp',PROJECTNAME+'.AppInstall', 'install')
    except:
        install=None

    if install:
        print >>out,'Custom Install:'
        res=install(self)
        if res:
            print >>out,res
        else:
            print >>out,'no output'
    else:
        print >>out,'no custom install'

    return out.getvalue()

def uninstall_actions(self):
    atool=self.portal_actions
    cptool=self.portal_controlpanel
    aitool=self.portal_actionicons
    
    existing_actions=[a.id for a in atool._cloneActions()]
    if 'acquisition' in existing_actions:
        atool.deleteActions([existing_actions.index('acquisition')])

    existing_actions=[a.id for a in cptool._cloneActions()]
    if 'overview_breakpoints' in existing_actions:
        cptool.deleteActions([existing_actions.index('overview_breakpoints')])

    if aitool.queryActionIcon('controlpanel','overview_breakpoints'):
        aitool.removeActionIcon('controlpanel','overview_breakpoints')


def uninstall(self):
    out = StringIO()
    
    #autouninstall tools
    for t in ['PloneSecurityInjector']:
        # undo: tools are not content. dont list it in navtree
        try:
            self.portal_properties.navtree_properties.metaTypesNotToList=list(self.portal_properties.navtree_properties.metaTypesNotToList)
            self.portal_properties.navtree_properties.metaTypesNotToList.remove(t)
        except ValueError:
            pass
        except:
            raise


    uninstall_actions(self)
    
    #try to call a custom uninstall method
    #in 'AppInstall.py' method 'uninstall'
    try:
        uninstall = ExternalMethod('temp','temp',PROJECTNAME+'.AppInstall', 'uninstall')
    except:
        uninstall=None

    if uninstall:
        print >>out,'Custom Uninstall:'
        res=uninstall(self)
        if res:
            print >>out,res
        else:
            print >>out,'no output'
    else:
        print >>out,'no custom uninstall'

    return out.getvalue()
