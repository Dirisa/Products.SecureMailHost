#
# Tests for Glossary types in the PHC
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneHelpCenter.tests import PHCTestCase


class TestGlossary(PHCTestCase.PHCTestCase):
    """General tests for Glossary and Definition objects."""

    def afterSetUp(self):
        self._createHelpCenter(self.folder, 'hc')
        self.gf = self.folder.hc.glossary
        self.gf.invokeFactory('HelpCenterDefinition', id='d')
        self.definition = self.gf.d

    def testInitialSections(self):
        # Test that the default section list is correct.
        self.assertEqual(self.definition.getSectionsVocab(), ('General',))

    def testVersionsonGlossary(self):
        versions = ('1.0','2.0','Strange version')
        self.folder.hc.setVersions_vocab(versions)
        newVersions = self.definition.getVersions_vocab()
        self.assertEqual(newVersions, versions)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGlossary))
    return suite

if __name__ == '__main__':
    framework()
