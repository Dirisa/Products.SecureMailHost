"""
$Id: test_factory.py,v 1.2 2005/03/09 18:00:43 dtremea Exp $
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneSoftwareCenter.tests import PSCTestCase

from Products.PloneSoftwareCenter.factory import Factory
from Products.PloneSoftwareCenter.factory import registerFactory
from Products.PloneSoftwareCenter.factory import getFactory
from Products.PloneSoftwareCenter.factory import factoryRegistry


class FooFactory(Factory):

    def __call__(self, context):
        if not 'foo' in context.objectIds():
            makeContent(context, portal_type='PSCRelease', id='foo')

class BarFactory(Factory):

    def __call__(self, context):
        if not 'bar' in context.objectIds():
            makeContent(context, portal_type='PSCRelease', id='bar')

class TestFactory(PSCTestCase.PSCTestCase):

    def test_factory(self):
        registerFactory('foo', FooFactory())
        registerFactory('bar', BarFactory())
        portal = self.getPortal()
        fp, fr, ff = populate(portal, 'Formulator', '1.6', 'formulator.tgz')
        fp.enableSettings(['foo'])
        self.failUnless(getattr(fp, 'foo', None))
        self.failUnless(fp.foo.portal_type == 'PSCRelease')
        # Just call again to make sure it doesn't
        # complain about enabling
        fp.enableSettings(['foo'])
        self.failUnless(list(fp.getSettings()) == ['foo'])
        fp.enableSettings(['bar'])
        self.failUnless(getattr(fp, 'bar', None))
        self.failUnless(fp.bar.portal_type == 'PSCRelease')
        self.failUnless(list(fp.getSettings()) == ['bar', 'foo'],
                        list(fp.getSettings()))
        # Just call again to make sure it doesn't
        # complain about enabling
        fp.enableSettings(['bar'])
        self.failUnless(list(fp.getSettings()) == ['bar', 'foo'],
                        list(fp.getSettings()))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Factory have been disabled.
    #suite.addTest(makeSuite(TestFactory))
    return suite

if __name__ == '__main__':
    framework()
