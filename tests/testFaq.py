#
# Tests for FAQ types in the PHC
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneHelpCenter.tests import PHCTestCase


class TestFaq(PHCTestCase.PHCTestCase):
    """General tests for FAQ Folder and FAQ objects."""

    def afterSetUp(self):
        self.folder.invokeFactory('HelpCenter', id='hc')
        self.ff = self.folder.hc.faq
        self.ff.invokeFactory('HelpCenterFAQ', id='f')
        self.faq = self.ff.f

    def testInitialSections(self):
        # Test that the default section list is correct.
        self.assertEqual(self.faq.getSectionsVocab(), ('General',))

    def testVersionsonFaq(self):
        versions = ('1.0','2.0','Strange version')
        self.folder.hc.setVersions_vocab(versions)
        newVersions = self.faq.getVersions_vocab()
        self.assertEqual(newVersions, versions)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFaq))
    return suite

if __name__ == '__main__':
    framework()
