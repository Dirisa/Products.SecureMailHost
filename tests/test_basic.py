"""
$Id: test_basic.py,v 1.1 2005/02/28 05:10:39 limi Exp $
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *
from DateTime.DateTime import DateTime

now = DateTime()

class TestBasic(ArcheSiteTestCase):

    def afterSetUp(self):
        self.login('manager')
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        qi.installProduct('PloneSoftwareCenter')

    def test_populate(self):
        fp, frf, fr, ff = populate(
                self.folder, 'Formulator', '1.6', 'formulator.tgz')
        self.assertEqual(ff.portal_type, 'PSCFile')
        self.assertEqual(frf.portal_type, 'PSCReleaseFolder')
        self.assertEqual(fr.portal_type, 'PSCRelease')
        self.assertEqual(fp.portal_type,'PSCProject')

    def test_release_folder(self):
        fp, frf, fr, ff = populate(
                self.folder, 'Formulator', '1.6', 'formulator.tgz')
        self.assertEqual(fp.getReleaseFolder(), frf)

    def test_latest_release(self):
        fp, frf, fr, ff = populate(
                self.folder, 'Formulator', '1.6', 'formulator.tgz')
        fr2 = new_release(frf, '1.7')
        self.assertEqual(fp.getLatestRelease(), fr2)
        fr.setEffectiveDate(now)
        self.assertEqual(fp.getLatestRelease(), fr)

    def test_unique_id(self):
        fp, frf, fr, ff = populate(
                self.folder, 'Formulator', '1.0', 'formulator.tgz')
        self.assertEqual(frf.generateUniqueId('PSCRelease'), "1.1")
        fr2 = new_release(frf, '2.7')
        self.assertEqual(frf.generateUniqueId('PSCRelease'), "2.8")

        
    def test_portalTypes(self):
        types = self.portal.portal_types
        self.failUnless('PloneSoftwareCenter' in types.objectIds())
        #self.failUnless('PSCProjectDependency' in types.objectIds())
        #self.failUnless('PSCProjectDependencyContainer' in types.objectIds())
        self.failUnless('PSCFile' in types.objectIds())
        self.failUnless('PSCRelease' in types.objectIds())
        self.failUnless('PSCImprovementProposal' in types.objectIds())
        self.failUnless('PSCImprovementProposalFolder' in types.objectIds())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBasic))
    return suite

if __name__ == '__main__':
    framework()
