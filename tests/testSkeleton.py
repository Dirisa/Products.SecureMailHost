import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.PloneClipboard.config import *
import common
common.installProducts()

class TestSomething(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        common.installWithinPortal(self.portal)

##     def testSomething(self):
##         self.assertEqual(2, 1+1)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestSomething))
        return suite
