import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.PloneClipboard.config import *
import Products.PloneClipboard.utils as utils

import common
common.installProducts()

class FakeResponse:
    def setCookie(*args, **kwargs): pass

class TestUtils(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        common.installWithinPortal(self.portal)

    def testSetQueryValues(self):
        before = 'there?a=1&b=2'
        after = utils.set_query_values(before, b=3, c=4)
        self.failUnless(after.startswith('there?a=1'))
        self.failIf(after.find('b=3') == -1)
        self.failIf(after.find('c=4') == -1)

    def testCopyObjectsByPath(self):
        ids = ['doc1', 'doc2']
        self.folder.invokeFactory('Folder', 'sub')
        sub = getattr(self.folder, 'sub')

        for id in ids:
            self.folder.invokeFactory('DDocument', id)

        self.folder.REQUEST = request = {}
        request['RESPONSE'] = FakeResponse()
        request['BASEPATH1'] = None

        paths = ['/portal/Members/test_user_1_/%s' % id for id in ids]
        cp = utils.copy_objects_by_path(self.folder, paths)

        sub.manage_pasteObjects(cp)
        self.assertEqual(sub.objectIds(), ids)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestUtils))
        return suite
