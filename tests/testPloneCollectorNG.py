#
# Test our OrderSupport implementation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase


ZopeTestCase.installProduct('PloneCollectorNG')

class TestOrderSupport(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # Get rid of the .personal subfolder
        membership = self.portal.portal_membership
        self.folder._delObject(membership.personal_id)
        # Add a bunch of subobjects we can order later on
        self.qi = self.portal.portal_quickinstaller
        print [p['id'] for p in self.qi.listInstalledProducts()]
        print '-'*8000
        print self.qi.installProducts(['PloneCollectorNG',])
        print [p['id'] for p in self.qi.listInstalledProducts()]
        import pdb
        pdb.set_trace()
        self.folder.invokeFactory('PloneCollectorNG', id='foo')



    def testInstallUninstallProduct(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOrderSupport))
    return suite

if __name__ == '__main__':
    framework()
