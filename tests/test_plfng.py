import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
from Testing import ZopeTestCase

# Install our product
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PloneLocalFolderNG')
ZopeTestCase.installProduct('PortalTransforms')

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.tests.utils import makeContent
from Products.CMFPlone.tests import PloneTestCase

SAMPLES = 'Products/PloneLocalFolderNG/tests/SamplesFiles/'
class BaseTest(PloneTestCase.PloneTestCase):
    samples_folder = os.path.join(os.environ.get('INSTANCE_HOME'), 
                                  *SAMPLES.split('/'))
                                   
    def afterSetUp(self):
        """ bootstrap test with a PLFNG """
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.loginPortalOwner()
        self.qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.qi.installProduct('Archetypes')
        self.at = getToolByName(self.portal, 'archetype_tool')
        self.qi.installProduct('PloneLocalFolderNG')
        self.at.manage_installType(typeName='PloneLocalFolderNG',
                                   package='PloneLocalFolderNG')

    def test_construction(self):
        """ ensure that we can create and see files """
        portal = self.portal
        folder = makeContent(portal, 'PloneLocalFolderNG', id='localfolder')
        folder.getField('folder').set(folder, self.samples_folder)
        self.failUnless(len(folder.contentValues()) != len(os.listdir(self.samples_folder)))

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseTest))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
