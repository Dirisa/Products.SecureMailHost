import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.PloneClipboard.config import *
import common
common.installProducts()

class TestReferenceBag(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        common.installWithinPortal(self.portal)
        ttool = self.portal.portal_types

        for id in ('doc1', 'doc2'):
            self.folder.invokeFactory('DDocument', id)
            setattr(self, id, getattr(self.folder, id))

        ttool.constructContent('BagCollection', self.folder, CLIPBOARDS_FOLDER)
        self.bagfolder = bagfolder = getattr(self.folder, CLIPBOARDS_FOLDER)

        for id in ('bag1', 'bag2'):
            bagfolder.invokeFactory('ReferenceBag', id)
            setattr(self, id, getattr(bagfolder, id))
        
    def testPasteAndClear(self):
        self.bag1.manage_pasteObjects(
            self.folder.manage_copyObjects(('doc1', 'doc2'))
            )

        self.bag2.manage_pasteObjects(
            self.folder.manage_copyObjects('doc2')
            )

        self.bag1.clear()
        # bag1 is empty
        self.assertEqual(self.bag1.objectIds(), [])
        # bag2 still contains one item
        self.assertEqual(len(self.bag2.objectIds()), 1)

    def testIsCopyBufferPasteable(self):
        cp = self.folder.manage_copyObjects('doc1')
        self.portal.REQUEST = {'__cp': cp}
        self.failUnless(self.bag1.isCopyBufferPasteable())

        self.portal.REQUEST = {}
        self.failIf(self.bag1.isCopyBufferPasteable())

        # Document is not referencable
        self.folder.invokeFactory('Document', 'doc3')
        cp = self.folder.manage_copyObjects('doc3')
        self.portal.REQUEST = {'__cp': cp}
        self.failIf(self.bag1.isCopyBufferPasteable())

    def testOneObjectTwoReferenceBags(self):
        for bag in (self.bag1, self.bag2):
            bag.manage_pasteObjects(
                self.folder.manage_copyObjects('doc1')
                )

        self.assertEqual(self.bag1.getRefs(), self.bag2.getRefs())

        self.bag1.manage_delObjects(['doc1'])
        # the reference containment in bag2 should not be affected
        self.assertEqual(len(self.bag2.objectIds()), 1)
        

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestReferenceBag))
        return suite
