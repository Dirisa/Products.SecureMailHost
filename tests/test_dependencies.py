"""
$Id: test_dependencies.py,v 1.2 2005/03/09 18:00:43 dtremea Exp $
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneSoftwareCenter.tests import PSCTestCase


class TestDependencies(PSCTestCase.PSCTestCase):

    def test_dependencies(self):
        portal = self.getPortal()
        fp, fr, ff = populate(portal, 'Formulator', '1.6', 'formulator.tgz')
        cp, cr, cf = populate(portal, 'CMFQuickInstallerTool', '1.0', 'cmfquick.tgz')
        p1, r1, fr1 = populate(portal)
        self.failUnless(getattr(r1, 'dependencies', None))
        self.assertRaises(ValueError, makeContent, r1, 'DependenciesFolder', 'deps')
        d1 = makeContent(r1.dependencies, portal_type='PSCProjectDependency', id='d1')
        d2 = makeContent(r1.dependencies, portal_type='PSCProjectDependency', id='d2')
        d1.setPackage(fp.UID())
        self.assertRaises(ValueError, d1.setRelease, 'non-existing-release')
        d1.setVersion(fr.UID())
        d1.setDependency_type('required')
        self.assertRaises(ValueError, d2.setPackage, fp.UID())
        d2.setPackage(cp.UID())
        d2.setRelease(cr.UID())
        d2.setDependency_type('required')
        self.failUnless(len(r1.dependencies.objectIds()) == 2)
        p2, r2, fr2 = populate(portal, release='2.1')
        self.failUnless(len(r2.dependencies.objectIds()) == 0)
        r2.populateFrom(r1.getId())
        self.failUnless(len(r2.dependencies.objectIds()) == 2)
        self.failUnless(len(r1.dependencies.objectIds()) == 2)
        refs1 = r1.dependencies.objectIds()
        refs2 = r2.dependencies.objectIds()
        self.failUnless(refs1 == refs2)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Dependencies have been disabled
    #suite.addTest(makeSuite(TestDependencies))
    return suite

if __name__ == '__main__':
    framework()
