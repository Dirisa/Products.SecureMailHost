#
# Tests for ErrorReference types in the PHC
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneHelpCenter.tests import PHCTestCase


class TestErrorReference(PHCTestCase.PHCTestCase):
    """General tests for ErrorReference Folder and ErrorReference objects."""

    def afterSetUp(self):
        self._createHelpCenter(self.folder, 'hc')
        self._createErrorReference(self.folder.hc.error, 'e')
        self.errorRef = self.folder.hc.error.e

    def testInitialSections(self):
        # Test that the default section list is correct.
        self.assertEqual(self.errorRef.getSectionsVocab(), ('General',))

    def testVersionsonErrorReference(self):
        versions = ('1.0','2.0','Strange version')
        self.folder.hc.setVersions_vocab(versions)
        newVersions = self.errorRef.getVersions_vocab()
        self.assertEqual(newVersions, versions)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestErrorReference))
    return suite

if __name__ == '__main__':
    framework()
