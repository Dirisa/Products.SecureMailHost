#
# Tests for Howto types in the PHC
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneHelpCenter.tests import PHCTestCase


class TestHowto(PHCTestCase.PHCTestCase):
    """General tests for Howto folder and HOWTO objects."""

    def afterSetUp(self):
        self.folder.invokeFactory('HelpCenter', id='hc')
        self.hf = self.folder.hc.howto
        self.hf.invokeFactory('HelpCenterHowTo', id='h')
        self.howto = self.hf.h

    def testVersionsHowto(self):
        versions = ('1.0','2.0','Strange version')
        self.folder.hc.setVersions_vocab(versions)
        newVersions = self.howto.getVersions_vocab()
        self.assertEqual(newVersions, versions)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestHowto))
    return suite

if __name__ == '__main__':
    framework()
