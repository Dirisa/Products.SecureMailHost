import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from SecurityInjectorTestCase import *
from Products.CMFCore.utils import getToolByName
from Products.PloneSecurityInjector.PloneSecurityInjector import PloneSecurityInjector
from zExceptions import Unauthorized

class TestTool(SecurityInjectorTestCase):

    def afterSetUp(self):
        SecurityInjectorTestCase.afterSetUp(self)
        ttool=self.portal.portal_types
        ttool.constructContent('Folder', container=self.portal, id='firstfolder')
        firstfolder=getattr(self.portal,'firstfolder')
        ttool.constructContent('Folder', container=firstfolder, id='secondfolder')
        secondfolder=getattr(firstfolder,'secondfolder')
        
    def testSecurityInjectorToolExists(self):
        sitool = getattr(self.portal, 'portal_securityinjector', None)
        self.assertNotEqual(sitool, None)
        self.failUnless(isinstance(sitool, PloneSecurityInjector))

    def testmanage_get_breakpoint(self):
        portal=self.portal
        sitool = getattr(portal, 'portal_securityinjector', None)
        sitool.doActionFor( portal.firstfolder, 'set_break',comment='' )

        self.failUnless( sitool.manage_get_breakpoint(portal.firstfolder), "manage_get_breakpoint return wrong value")

        sitool.doActionFor( portal.firstfolder, 'remove_break', comment='' )

        self.failUnless( sitool.manage_get_breakpoint(portal.firstfolder), 'manage_get_breakpoint return wrong value')

    def testgetWorkflowFor(self):
        portal=self.portal
        sitool = getattr(portal, 'portal_securityinjector', None)
        self.assertEqual('securityinjector_workflow' in sitool.getWorkflowFor(portal.firstfolder), True)
 
    def testcheck_local_roles(self):
        portal=self.portal
        sitool = getattr(portal, 'portal_securityinjector', None)
        mtool = portal.portal_membership
        user=portal.portal_membership.getMemberById('test1')
        
        self.failUnlessRaises(Unauthorized, sitool.check_local_roles, user, portal.firstfolder)

        mtool.setLocalRoles(portal.firstfolder,member_ids=['test1'],member_role='Reviewer')

        self.failUnlessRaises(Unauthorized, sitool.check_local_roles, user, portal.firstfolder)

    def testcheck_local_roles(self):
        portal=self.portal
        sitool = getattr(portal, 'portal_securityinjector', None)
        self.assertEqual(sitool.get_all_group_members('group_g1'),['test1','test2'])

    def testsort_member_to_roles(self):
        portal=self.portal
        sitool = getattr(portal, 'portal_securityinjector', None)
        local_roles=(('test1',('r1','r2','r3')),('test2',('r5','r6')),('group_g1',('r7',)))
        sorted_roles=sitool.sort_member_to_roles(local_roles)
        self.assertEqual(sorted_roles,{'test1':['r1','r2','r3','r7'],'test2':['r5','r6','r7']})
        
if __name__ == '__main__':
    framework()
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestTool))
        return suite

