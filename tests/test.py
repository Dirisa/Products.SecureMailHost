import unittest
import Zope     # product initialization
root = Zope.app()
from Acquisition import aq_base
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.Archetypes.Extensions.Install import install as install_archetypes
from Products.CMFMember.Extensions.Install import install as install_cmfmember

from AccessControl.SecurityManagement import newSecurityManager

import sys

site = 'testsite'

class CMFMemberTest( SecurityRequestTest ):

    def setUp( self ):
        SecurityRequestTest.setUp(self)
        # create an admin user
        self.root.acl_users.userFolderAddUser('admin', 'qwerty', ('Manager','Member',), ())
        get_transaction().commit()
        # assume role of admin
        newSecurityManager(None, self.root.acl_users.getUser('admin').__of__(self.root.acl_users))

        if hasattr(self.root, site):
            self.root.manage_delObjects([site])
            get_transaction().commit()
        self.root.manage_addProduct[ 'CMFPlone' ].manage_addSite( site )
        get_transaction().commit()

        self.testsite = getattr(self.root, site)

        install_archetypes(self.testsite)
        install_cmfmember(self.testsite)

        self.id = 'test_member'
        self.password = 'password'
        self.roles = ('Member',)
        self.domains = ('127.0.0.1',)

        # add a new member
        newSecurityManager(None, self.root.acl_users.getUser('admin').__of__(self.root.acl_users))

        self.testsite.portal_membership.addMember(self.id, self.password, self.roles, self.domains)
        self.user = self.testsite.acl_users.getUser(self.id)
        # force creation of user via wrapUser
        self.member = self.testsite.portal_membership.getMemberById(self.id)

        self.root_id = 'root_member'
        self.root_password = 'root_password'
        self.root_roles = ('Manager','Reviewer','Member',)
        self.root_domains = ('127.0.0.1',)

        self.root.acl_users.userFolderAddUser(self.root_id, self.root_password, self.root_roles, self.root_domains)
        self.root_user = self.root.acl_users.getUser(self.root_id)

        newSecurityManager(None, self.root_user.__of__(self.root.acl_users))
        # force creation of user via wrapUser
        self.root_member = self.testsite.portal_membership.getAuthenticatedMember()
        
        newSecurityManager(None, self.root.acl_users.getUser('admin').__of__(self.root.acl_users))

        # create some content
        user = self.user.__of__(self.testsite.acl_users)
        root_user = self.root_user.__of__(self.root.acl_users)
        self.testsite.invokeFactory(id='folder1', type_name='Folder')
        folder1 = getattr(self.testsite, 'folder1')
        folder1.changeOwnership(user)
        folder1.manage_addLocalRoles(self.root_id, ('Reviewer',))
        
        folder1.invokeFactory(id='doc1', type_name='Document')
        doc1 = getattr(folder1, 'doc1')
        doc1.changeOwnership(user)

        folder1.invokeFactory(id='doc2', type_name='Document')
        doc2 = getattr(folder1, 'doc2')
        doc2.changeOwnership(root_user)

        self.testsite.invokeFactory(id='folder2', type_name='Folder')
        folder2 = getattr(self.testsite, 'folder2')
        folder2.changeOwnership(root_user)
        folder2.manage_addLocalRoles(self.id, ('Reviewer',))

        folder2.invokeFactory(id='doc3', type_name='Document')
        doc3 = getattr(folder2, 'doc3')
        doc3.changeOwnership(user)

        folder2.invokeFactory(id='doc4', type_name='Document')
        doc4 = getattr(folder2, 'doc4')
        doc4.changeOwnership(root_user)
        
        get_transaction().commit()

        self.assertEqual(doc2.getOwner(0), self.root_user)
        folder1.changeOwnership(user)
        doc2 = getattr(folder1, 'doc2')
        self.assertEqual(doc2.getOwner(0), self.root_user)

    def tearDown( self ):
        self.member = None
        self.root_member = None
        self.testsite = None

        if hasattr(self.root, site):
            self.root.manage_delObjects([site])
            get_transaction().commit()
        SecurityRequestTest.tearDown(self)


    def test_user(self):
        # make sure all the member properties we set are correct
        self.failUnless(self.member != None)
        self.assertEqual(self.member.getMemberId(), self.id)
        self.assertEqual(self.member._getPassword(), self.password)
        self.assertEqual(self.member.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(self.member.getDomains(), self.domains)

        # grab the user
        user = self.member.getUser()
        self.assertEqual(user, self.user)
        # make sure the user properties are correct
        self.assertEqual(user.getId(), self.id)
        self.assertEqual(user._getPassword(), self.password)
        self.assertEqual(user.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(user.getDomains(), self.domains)

        password2 = 'password2'
        self.member._setPassword(password2)
        self.assertEqual(self.member._getPassword(), password2)
        self.member.setRoles('Member,Manager')
        self.assertEqual(self.member.getRoles(), ('Member','Manager','Authenticated'))
        self.member.setDomains('127.0.0.1\r\n127.0.0.2\r\n  ')
        self.assertEqual(self.member.getDomains(), ('127.0.0.1','127.0.0.2'))


    def test_delete(self):
        self.testsite.portal_memberdata.manage_delObjects([self.id])

        # make sure old member is gone
        member = self.testsite.portal_membership.getMemberById(self.id)
        self.assertEqual(member, None)

        # make sure member has been moved
        user = self.testsite.acl_users.getUser(self.id)
        self.assertEqual(user, None)

        # make sure appropriate content has been deleted
        folder1 = getattr(self.testsite, 'folder1', None)
        self.assertEqual(folder1, None)

        folder2 = getattr(self.testsite, 'folder2', None)
        self.failUnless(folder2 != None)

        doc3 = getattr(folder2, 'doc3', None)
        self.assertEqual(doc3, None)

        doc4 = getattr(folder2, 'doc4', None)
        self.failUnless(doc4 != None)

        # make sure local roles get deleted
        roles = folder2.get_local_roles_for_userid(self.id)
        self.assertEqual(roles, ())

    def test_deleteRoot(self):
        # a more complicated case -- the authenticated user lives in self.root.acl_users, not portal.acl_users

        self.testsite.portal_memberdata.manage_delObjects([self.root_id])

        # make sure old member is gone
        member = self.testsite.portal_membership.getMemberById(self.root_id)
        self.assertEqual(member, None)

        # make sure member has been moved
        user = self.root.acl_users.getUser(self.root_id)
        self.failUnless(user != None)
        self.assertEqual(user, self.root_user)

        # make sure appropriate content has been deleted
        folder1 = getattr(self.testsite, 'folder1', None)
        self.failUnless(folder1 != None)

        folder2 = getattr(self.testsite, 'folder2', None)
        self.assertEqual(folder2, None)

        doc1 = getattr(folder1, 'doc1', None)
        self.failUnless(doc1 != None)

        doc2 = getattr(folder1, 'doc2', None)
        self.assertEqual(doc2, None)


    def test_rename(self):
        new_id = 'id2'
        self.testsite.portal_memberdata.manage_renameObjects((self.id,),(new_id,))

        # make sure member has been moved
        member = self.testsite.portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member._getPassword(), self.password)
        self.assertEqual(member.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.domains)

        # make sure old member is gone
        member = self.testsite.portal_membership.getMemberById(self.id)
        self.assertEqual(member, None)

        # make sure member has been moved
        user = self.testsite.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.password)
        self.assertEqual(user.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(user.domains, self.domains)

        # make sure old user is gone
        user = self.testsite.acl_users.getUser(self.id)
        self.assertEqual(user, None)

        # make sure appropriate ownership changes have been made
        user = self.testsite.acl_users.getUser(new_id)

        folder1 = getattr(self.testsite, 'folder1', None)
        self.failUnless(folder1 != None)
        owner = folder1.getOwner(0)
        self.failUnless(owner == user)
        
        doc1 = getattr(folder1, 'doc1', None)
        self.failUnless(doc1 != None)
        owner = doc1.getOwner(0)
        self.failUnless(owner == user)

        # make sure doc2 is untouched
        doc2 = getattr(folder1, 'doc2', None)
        self.failUnless(doc2 != None)
        owner = doc2.getOwner(0)
        self.failUnless(owner == self.root_user)

        folder2 = getattr(self.testsite, 'folder2', None)
        self.failUnless(folder2 != None)
        owner = folder2.getOwner(0)
        self.failUnless(owner == self.root_user)

        doc3 = getattr(folder2, 'doc3', None)
        self.failUnless(doc3 != None)
        owner = doc3.getOwner(0)
        self.failUnless(owner == user)

        doc4 = getattr(folder2, 'doc4', None)
        self.failUnless(doc4 != None)
        owner = doc4.getOwner(0)
        self.failUnless(owner == self.root_user)

        # make sure local roles get updated
        roles = folder1.get_local_roles_for_userid(self.root_id)
        self.assertEqual(roles, ('Reviewer',))

        roles = folder2.get_local_roles_for_userid(self.id)
        self.assertEqual(roles, ())

        roles = folder2.get_local_roles_for_userid(new_id)
        self.assertEqual(roles, ('Reviewer',))


    # a more complicated case -- the authenticated user lives in self.root.acl_users, not portal.acl_users
    def test_renameRoot(self):
        new_id = 'id2'
        self.testsite.portal_memberdata.manage_renameObjects((self.root_id,),(new_id,))

        # make sure member has been moved
        member = self.testsite.portal_membership.getMemberById(new_id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member._getPassword(), self.root_password)
        self.assertEqual(member.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_domains)

        # make sure old member is gone
        member = self.testsite.portal_membership.getMemberById(self.root_id)
        self.assertEqual(member, None)

        # make sure member has been copied
        user = self.testsite.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_password)
        self.assertEqual(user.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(user.domains, self.root_domains)

        # make sure old user is still there gone
        user = self.root.acl_users.getUser(self.root_id)
        self.failUnless(user != None)
        self.assertEqual(user, self.root_user)


        # make sure appropriate ownership changes have been made
        user = self.testsite.acl_users.getUser(new_id)

        folder1 = getattr(self.testsite, 'folder1', None)
        self.failUnless(folder1 != None)
        owner = folder1.getOwner(0)
        self.failUnless(owner == self.user)
        
        doc1 = getattr(folder1, 'doc1', None)
        self.failUnless(doc1 != None)
        owner = doc1.getOwner(0)
        self.failUnless(owner == self.user)

        # make sure doc2 is untouched
        doc2 = getattr(folder1, 'doc2', None)
        self.failUnless(doc2 != None)
        owner = doc2.getOwner(0)
        self.failUnless(owner == user)

        folder2 = getattr(self.testsite, 'folder2', None)
        self.failUnless(folder2 != None)
        owner = folder2.getOwner(0)
        self.failUnless(owner == user)

        doc3 = getattr(folder2, 'doc3', None)
        self.failUnless(doc3 != None)
        owner = doc3.getOwner(0)
        self.failUnless(owner == self.user)

        doc4 = getattr(folder2, 'doc4', None)
        self.failUnless(doc4 != None)
        owner = doc4.getOwner(0)
        self.failUnless(owner == user)

        # make sure local roles get updated
        roles = folder2.get_local_roles_for_userid(self.id)
        self.assertEqual(roles, ('Reviewer',))

        roles = folder1.get_local_roles_for_userid(self.root_id)
        self.assertEqual(roles, ())

        roles = folder1.get_local_roles_for_userid(new_id)
        self.assertEqual(roles, ('Reviewer',))


    def test_copy(self):
        cb_copy_data = self.testsite.portal_memberdata.manage_copyObjects((self.id,))
        self.testsite.portal_memberdata.manage_pasteObjects(cb_copy_data)

        # make sure old member and user are still there
        member = self.testsite.portal_membership.getMemberById(self.id)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), self.id)
        self.assertEqual(member._getPassword(), self.password)
        self.assertEqual(member.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.domains)

        user = self.testsite.acl_users.getUser(self.id)
        self.assertEqual(user, self.user)

        new_id = 'copy_of_' + self.id
        # make sure member has been copied
#        member = self.testsite.portal_membership.getMemberById(new_id)
        member = self.testsite.portal_memberdata.get(new_id, None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member._getPassword(), self.password)
        self.assertEqual(member.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.domains)

        user = self.testsite.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.password)
        self.assertEqual(user.getRoles(), self.roles + ('Authenticated',))
        self.assertEqual(user.domains, self.domains)


    def test_copy_root(self):
        cb_copy_data = self.testsite.portal_memberdata.manage_copyObjects((self.root_id,))
        self.testsite.portal_memberdata.manage_pasteObjects(cb_copy_data)

        # make sure old member and user are still there
#        member = self.testsite.portal_membership.getMemberById(self.root_id)
        member = self.testsite.portal_memberdata.get(self.root_id, None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), self.root_id)
        self.assertEqual(member._getPassword(), self.root_password)
        self.assertEqual(member.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_domains)

        user = self.root.acl_users.getUser(self.root_id)
        self.assertEqual(user, self.root_user)

        new_id = 'copy_of_' + self.root_id
        # make sure member has been copied
#        member = self.testsite.portal_membership.getMemberById(new_id)
        member = self.testsite.portal_memberdata.get(new_id, None)
        self.failUnless(member != None)
        self.assertEqual(member.getMemberId(), new_id)
        self.assertEqual(member._getPassword(), self.root_password)
        self.assertEqual(member.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(member.getDomains(), self.root_domains)

        user = self.testsite.acl_users.getUser(new_id)
        self.failUnless(user != None)
        self.assertEqual(user.__, self.root_password)
        self.assertEqual(user.getRoles(), self.root_roles + ('Authenticated',))
        self.assertEqual(user.domains, self.root_domains)

        user = self.root.acl_users.getUser(new_id)
        self.assertEqual(user, None)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CMFMemberTest),
        ))

if __name__ == '__main__':
    unittest.main()