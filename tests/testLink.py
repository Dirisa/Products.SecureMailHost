#
# Tests for Link types in the PHC
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneHelpCenter.tests import PHCTestCase


class TestLink(PHCTestCase.PHCTestCase):
    """General tests for Link Folder and Link objects."""

    def afterSetUp(self):
        self._createHelpCenter(self.folder, 'hc')
        self.lf = self.folder.hc.link
        self.lf.invokeFactory('HelpCenterLink', id='l')
        self.link = self.lf.l

    def testInitialSections(self):
        # Test that the default section list is correct.
        self.assertEqual(self.link.getSectionsVocab(), ('General',))

    def testVersionsonLink(self):
        versions = ('1.0','2.0','Strange version')
        self.folder.hc.setVersions_vocab(versions)
        newVersions = self.link.getVersions_vocab()
        self.assertEqual(newVersions, versions)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLink))
    return suite

if __name__ == '__main__':
    framework()
