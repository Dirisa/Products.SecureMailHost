from Testing import ZopeTestCase
from OFS.ObjectManager import BadRequestException
from Products.CMFPlone.tests import PloneTestCase

from AccessControl.SecurityManagement import newSecurityManager
from Products.Archetypes.Extensions.Install import install as install_archetypes

portal_name  = 'portal'
portal_owner = 'portal_owner'
default_user = 'unittest_admin'

ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFActionIcons')
ZopeTestCase.installProduct('CMFQuickInstallerTool')
ZopeTestCase.installProduct('CMFFormController')
ZopeTestCase.installProduct('ZCTextIndex')
ZopeTestCase.installProduct('CMFPlone')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('DaytaTool')
ZopeTestCase.installProduct('PloneSecurityInjector')
ZopeTestCase.installProduct('PloneSecurityInjectorWorkflow')

class SecurityInjectorTestCase(PloneTestCase.PloneTestCase):

    def installProducts(self, products=[]):
        self.portal.portal_quickinstaller.installProducts(products=products, stoponerror=1)

    def afterSetUp( self ):
        #install AquisitionNG
        #create testing user
        self.loginPortalOwner()
        install_archetypes(self.portal)
        self._refreshSkinData()
        self.installProducts(products=['PloneSecurityInjector'])
        self.installProducts(products=['PloneSecurityInjectorWorkflow'])
        self.uf = self.portal.acl_users
        self.uf._doAddGroup('g1', ())
        self.uf._doAddGroup('g2', ())
        self.uf._doAddUser('test1', 'test', ('Reviewer',), (), ('g1','g2'), )
        self.uf._doAddUser('test2', 'test', ('Reviewer',), (), ('g1',), )
