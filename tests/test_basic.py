"""
$Id: test_basic.py,v 1.2 2005/03/09 18:00:43 dtremea Exp $
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneSoftwareCenter.tests import PSCTestCase

from Products.PloneSoftwareCenter import config


class TestPortalTypes(PSCTestCase.PSCTestCase):

    def afterSetUp(self):
        self.types = self.portal.portal_types.objectIds()

    def testPortalTypesExists(self):
        types = [
            'PloneSoftwareCenter',
            'PSCProject',
            'PSCImprovementProposalFolder',
            'PSCImprovementProposal',
            'PSCReleaseFolder',
            'PSCRelease',
            'PSCFile',
            'PSCFileLink',
        ]
        for t in types:
            self.failUnless(t in self.types, 'Type not installed: %s' % t)

    def testPSCAllowedTypes(self):
        psc = self.portal.portal_types.getTypeInfo('PloneSoftwareCenter')
        self.failUnless('PSCProject' in psc.allowed_content_types)
        self.failUnlessEqual(len(psc.allowed_content_types), 1)


class TestFolderContainment(PSCTestCase.PSCTestCase):

    def afterSetUp(self):
        # XXX: Check with restricted permissions later
        self.setRoles(['Manager'])
        self.folder.invokeFactory('PloneSoftwareCenter', id='psc')

    def testPSCContainment(self):
        self.folder.psc.invokeFactory('PSCProject', id='p')
        self.failUnless('p' in self.folder.psc.objectIds())
        p_ids = self.folder.psc.p.objectIds()
        self.failUnless(config.RELEASES_ID in p_ids)
        self.failUnless(config.IMPROVEMENTS_ID in p_ids)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalTypes))
    suite.addTest(makeSuite(TestFolderContainment))
    return suite

if __name__ == '__main__':
    framework()
