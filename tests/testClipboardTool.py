import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base

from Products.PloneClipboard.config import *
import common
common.installProducts()

class TestClipboardTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        common.installWithinPortal(self.portal)
        self.tool = getattr(self.portal, TOOLNAME)

    def _getHomeFolder(self):
        return self.portal.portal_membership.getHomeFolder()

    def testGetClipboardsNoCreate(self):
        self.assertEqual(self.tool.getClipboards(), [])
        home = self.portal.portal_membership.getHomeFolder()
        self.failIf(hasattr(aq_base(home), CLIPBOARDS_FOLDER))

    def testGetClipboardsAnonymous(self):
        self.logout()
        self.assertEqual(self.tool.getClipboards(), None)

    def testGetClipboardsCreate(self):
        cb = self.tool.getClipboards(create=1)
        home = self._getHomeFolder()

        self.failUnless(hasattr(aq_base(home), CLIPBOARDS_FOLDER))

        folder = getattr(home, CLIPBOARDS_FOLDER)
        self.assertEqual(folder.contentIds(), ['A', 'B', 'C'])

    def testGetClipboardsFolderExists(self):
        home = self._getHomeFolder()
        home.invokeFactory('Folder', CLIPBOARDS_FOLDER)

        self.assertEqual(self.tool.getClipboards(), [])
        # no muck around with clipboards if CLIPBOARDS_FOLDER exists
        self.assertEqual(self.tool.getClipboards(create=1), [])

    def testGetClipboard(self):
        self.testGetClipboardsCreate()
        self.failUnless(self.tool.getClipboard('C'))
        self.failIf(self.tool.getClipboard('E'))
    
    def testCreateClipboard(self):
        refbag = self.tool.createClipboard('A')
        self.assertEqual(refbag.meta_type, 'ReferenceBag')
        cb = self.tool.getClipboards(create=1)
        self.assertEqual(len(cb), 1)
        self.assertEqual(cb[0].getId(), 'A')

    def testClipboardWorkflow(self):
        self.testCreateClipboard()
        wtool = self.portal.portal_workflow
        cb = self.tool.getClipboards()[0]
        self.assertEqual(wtool.getInfoFor(cb, 'review_state'), 'private')

        home = self._getHomeFolder()
        folder = getattr(home, CLIPBOARDS_FOLDER)
        self.assertEqual(wtool.getInfoFor(folder, 'review_state'), 'private')
        
    def testCreateDefaultClipboards(self):
        self.testCreateClipboard()
        self.tool.createDefaultClipboards()
        home = self._getHomeFolder()

        folder = getattr(home, CLIPBOARDS_FOLDER)
        self.assertEqual(folder.contentIds(), ['A', 'B', 'C'])

    def testCreateDefaultClipboardsDeleteAndGetClipboardsCreate(self):
        self.testCreateDefaultClipboards()
        home = self._getHomeFolder()

        folder = getattr(home, CLIPBOARDS_FOLDER)
        folder.manage_delObjects(folder.contentIds())

        self.assertEqual(self.tool.getClipboards(), [])
        home.manage_delObjects([CLIPBOARDS_FOLDER])

        self.assertEqual(self.tool.getClipboards(), [])
        boards = self.tool.getClipboards(create=1)
        self.assertEqual([b.getId() for b in boards], ['A', 'B', 'C'])
        
    def testCreateDefaultClipboardsFail(self):
        self.logout()
        self.assertRaises(AttributeError, self.tool.createDefaultClipboards)

    def testGetClipboardsAfterCreate(self):
        self.testCreateClipboard()
        cb = self.tool.getClipboards(create=1)
        home = self._getHomeFolder()

        folder = getattr(home, CLIPBOARDS_FOLDER)
        self.assertEqual(folder.contentIds(), ['A'])


if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestClipboardTool))
        return suite
