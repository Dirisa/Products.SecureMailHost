#                                                       #
#                 Test GroupUserFolder                  #
#                                                       #
#                                                       #
# (c)2002 Ingeniweb                                     #

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))



# Load fixture
from Testing import ZopeTestCase

# Permissions / security
from AccessControl.Permissions import access_contents_information, view, add_documents_images_and_files, change_images_and_files, view_management_screens
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager, getSecurityManager
from AccessControl import Unauthorized
from AccessControl.User import UnrestrictedUser

import urllib

# Create the error_log object
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.close(app)

# Start the web server
host, port = ZopeTestCase.utils.startZServer(4)
base = 'http://%s:%d/%s' %(host, port, ZopeTestCase._folder_name)


# Get global vars
#from Products.GroupUserFolder.global_symbols import *
from Products.GroupUserFolder.interfaces import IUserFolder
from Interface import Verify

# Install our product
ZopeTestCase.installProduct('GroupUserFolder')
ZopeTestCase.installProduct('OFSP')

import GRUFTestCase
from Log import *


class TestGroupUserFolder(GRUFTestCase.GRUFTestCase):

    #                                                   #
    #           Basic GRUF behaviour testing            #
    #                                                   #

    def test00userNames(self,):
        """
        test00userNames(self,)
        Basic test of user and group names.
        """
        un = self.gruf_folder.acl_users.getUserNames()
        users = [
            'g1', 'g2', "g3", "g4",
            "ng1", "ng2", "ng3", "ng4", "ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "extranet", "intranet", "compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))
        

    def test00userIds(self,):
        """
        test00userIds(self,)
        Basic test of user and group names.
        """
        un = self.gruf.getUserIds()
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))


    #                                                   #
    #           Basic GRUF behaviour testing            #
    #                                                   #

    def test01userRoles(self,):
        """
        test01userRoles => Test if the user "inherits" group roles
        """
        # Add a few roles
        if not "userrole" in self.gruf.userFolderGetRoles():
            self.gruf.userFolderAddRole("userrole")
        if not "grouprole" in self.gruf.userFolderGetRoles():
            self.gruf.userFolderAddRole("grouprole")

        # Add the group & the user
        self.gruf.userFolderAddGroup(
            name = 'gtest',
            roles = ['grouprole', ],
            )
        self.gruf.userFolderAddUser(
            name = 'utest',
            password = 'secret',
            roles = ('userrole', ),
            groups = ('gtest', ),
            )

        # Check if the user has the right roles
        usr = self.gruf.getUser('utest')
        roles = usr.getRoles()
        self.failUnless('Authenticated' in roles)
        self.failUnless('userrole' in roles)
        self.failUnless('grouprole' in roles)

        # Remove the group & user
        self.gruf.userFolderDelUsers(['utest',])
        self.gruf.userFolderDelGroups(['gtest',])

    def test02securityMatrix(self,):
        """
        test02securityMatrix(self,) => Test the whole security matrix !

        We just check that people has the right roles
        """
        self.failUnless(self.compareRoles(None, "u1", ()))
        self.failUnless(self.compareRoles(None, "u2", ()))
        self.failUnless(self.compareRoles(None, "u3", ("r1", )))
        self.failUnless(self.compareRoles(None, "u4", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u5", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u6", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u7", ("r1", "r2", "r3", )))


    def test03usersBelongToGroups(self,):
        """
        test03usersBelongToGroups(self,) => test that the users belong to the right groups.
        This implies nested groups testing
        """
        # Check regular users
        self.failUnless(self.compareGroups("u1", ()))
        self.failUnless(self.compareGroups("u2", ("g1", )))
        self.failUnless(self.compareGroups("u3", ("g1", "g2", )))
        self.failUnless(self.compareGroups("u4", ("g1", "g2", "g3", )))
        self.failUnless(self.compareGroups("u5", ("g2", "g3", )))
        self.failUnless(self.compareGroups("u6", ("g3", )))
        self.failUnless(self.compareGroups("u7", ("g4", )))

        # Check nested groups
        self.failUnless(self.compareGroups("group_ng1", ("g1", )))
        self.failUnless(self.compareGroups("group_ng2", ("g2", "g3", )))
        self.failUnless(self.compareGroups("group_ng3", ("g2", "g3", "ng2", )))
        self.failUnless(self.compareGroups("group_ng4", ("g2", "g3", "ng2", )))
        self.failUnless(self.compareGroups("group_ng5", ("g2", "g3", "ng2", "ng4", )))
##        self.failUnless(self.compareGroups("ng6", ("ng5", )))

        # Check nested-groups users
        self.failUnless(self.compareGroups("u8", ("ng1", "g1", )))
        self.failUnless(self.compareGroups("u9", ("ng2", "g1", "g2","g3",  )))
        self.failUnless(self.compareGroups("u10", ("ng2", "ng3", "g2", "g3", )))
        self.failUnless(self.compareGroups("u11", ("ng2", "ng3", "g2", "g3", )))
##        self.failUnless(self.compareGroups("u12", ()))


    def test04localRoles(self,):
        """
        Test the security matrix on a local role

        We just check that people has the right roles
        """
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u1", ()))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u2", ("r3", )))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u3", ("r1", "r3", )))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u4", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u5", ("r1", "r2", )))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u6", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u7", ("r1", "r2", "r3", )))


    def test05nestedGroups(self,):
        """
        Test security on nested groups
        """
        # Test group roles
        self.failUnless(self.compareRoles(None, "group_ng1", ()))
        self.failUnless(self.compareRoles(None, "group_ng2", ('r1', 'r2', )))
        self.failUnless(self.compareRoles(None, "group_ng3", ('r1', 'r2', )))
        self.failUnless(self.compareRoles(None, "group_ng4", ('r1', 'r2', 'r3', )))
        self.failUnless(self.compareRoles(None, "group_ng5", ('r1', 'r2', 'r3', )))
##        self.failUnless(self.compareRoles(None, "group_ng6", ()))

        # Test user roles
        self.failUnless(self.compareRoles(None, "u8", ()))
        self.failUnless(self.compareRoles(None, "u9", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u10", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u11", ("r1", "r2", "r3")))
##        self.failUnless(self.compareRoles(None, "u12", ("r1", "r2", "r3")))

        # Test the same with local roles (wow !)
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u8", ("r3", )))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u9", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u10", ("r1", "r2", )))
        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u11", ("r1", "r2", "r3")))
##        self.failUnless(self.compareRoles(self.gruf_folder.lr, "u12", ("r1", "r2", "r3")))


    def test06doubleNesting(self,):
        """
        Test against double nesting
        """
        self.failUnless(self.compareGroups("group_compta", ('intranet', 'extranet', )))


    def test08traversal(self,):
        """
        test traversal to ensure management screens are correctly accessible
        """
        # Check if we can traverse a GRUF to fetch a user (check a dummy method on it)
        traversed = self.gruf.restrictedTraverse("u1")
        Log(LOG_DEBUG, traversed)
        self.failUnless(traversed.meta_type == "Group User Folder")

        # Now, do the same but with a folder of the same name
        self.gruf_folder.manage_addProduct['OFSP'].manage_addFolder('u1')
        traversed = self.gruf.restrictedTraverse("u1")
        Log(LOG_DEBUG, traversed)
        self.failUnless(traversed.meta_type == "Group User Folder")


    #                                                   #
    #               GRUF Interface testing              #
    #                                                   #

    def test10GRUFMethods(self,):
        """
        We test that GRUF's API is well protected
        """
        self.assertRaises(Unauthorized, self.gruf_folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')
        self.assertRaises(Unauthorized, self.gruf_folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')
        #urllib.urlopen(base+'/acl_users/getGRUFId')



    #                                                   #
    #              Classical security testing           #
    #                                                   #

##    def testAccess(self):
##        '''Test access'''
##        page = self.gruf_folder(self.gruf_folder)

##    def testWeb(self):
##        '''Test web access'''
##        urllib._urlopener = GRUFTestCase.UnauthorizedOpener()
##        Log(LOG_DEBUG, base)
##        page = urllib.urlopen(base).read()
##        if page.find('Resource not found') >= 0:
##            self.fail('Resource not found')

##    def testWeb2(self):
##        '''Test web access to protected resource'''
##        urllib._urlopener = GRUFTestCase.ManagementOpener()
##        page = urllib.urlopen(base+'/secret_html').read()
##        if page.find('Resource not found') >= 0:
##            self.fail('Resource not found')

##    def testSecurity(self):
##        '''Test security of public resource'''
##        # Should be accessible
##        try: self.gruf_folder.restrictedTraverse('index_html')
##        except Unauthorized: self.fail('Unauthorized')

##    def testSecurity2(self):
##        '''Test security of protected resource'''
##        # Should be protected
##        self.assertRaises(Unauthorized, self.gruf_folder.restrictedTraverse, 'secret_html')

##    def testWebSecurity(self):
##        '''Test web security of public resource'''
##        # Should be accessible
##        urllib._urlopener = GRUFTestCase.UnauthorizedOpener()
##        try: urllib.urlopen(base+'/index_html')
##        except Unauthorized: self.fail('Unauthorized')

##    def testWebSecurity2(self):
##        '''Test web security of protected resource'''
##        # Should be protected
##        urllib._urlopener = GRUFTestCase.UnauthorizedOpener()
##        try:
##            urllib.urlopen, base+'/secret_html'
##        except Unauthorized:
##            pass

##    def testAbsoluteURL(self):
##        '''Test absolute_url'''
##        self.assertEquals(self.gruf_folder.absolute_url(), base)




#                                                   #
#                 Copy / Paste support              #
#                                                   #

class TestGroupUserFolderCopy(TestGroupUserFolder):
    """
    Same tests as the previous class, but AFTER a copy/paste operation
    """
    _setup_done = 0

    def afterSetUp(self,):
        """
        afterSetUp(self,) => Basic gruf setup with a copy/paste
        """
        # Build a security context with the regular GRUF Folder
        self.gruf_setup()
        self.security_context_setup()

        # Perform tests to ensure using GRUF and filling all caches
        self.test00userNames()
        self.test01userRoles()
        self.test02securityMatrix()
        self.test03usersBelongToGroups()
        self.test04localRoles()
        self.test05nestedGroups()
        self.test06doubleNesting()

        # Now copy/paste a re-build the security context in another folder
        self._setupUser()
        self._setRoles(['Manager', ], )
        self._login()
        self.folder.manage_addProduct['OFSP'].manage_addFolder('gruf_folder2')
        folder2 = self.folder.gruf_folder2

        # copy/paste GRUF inside
        copy = self.gruf_folder.manage_copyObjects(ids = ['acl_users',],)
        folder2.manage_pasteObjects(cb_copy_data = copy)



if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestGroupUserFolder))
        suite.addTest(unittest.makeSuite(TestGroupUserFolderCopy))
        return suite
