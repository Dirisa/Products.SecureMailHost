#
# Tests for workflow and permissions in the PHC
#

import os, sys

from Products.PloneTestCase.PloneTestCase import default_user

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneHelpCenter.tests import PHCTestCase


class TestWorkflow(PHCTestCase.PHCTestCase):
    """Tests for workflow specific issues in the PHC."""

    def afterSetUp(self):
        self._createHelpCenter(self.folder, 'hc')
        pm = self.portal.portal_membership
        pm.addMember( 'test_reviewer', 'pw', ['Member', 'Reviewer'], [] )
        
    def testEditPublishedHowto(self):
        newBody = 'Changed to this content while published.'
        howto = self._createHowto(self.folder.hc.howto, 'howto1')
        self.portal.portal_workflow.doActionFor(howto, 'submit')
        self.login('test_reviewer')
        self.portal.portal_workflow.doActionFor(howto, 'publish')
        self.login(default_user)
        howto.edit(text_format='plain', body=newBody)
        self.assertEqual(howto.getRawBody(), newBody)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkflow))
    return suite

if __name__ == '__main__':
    framework()
