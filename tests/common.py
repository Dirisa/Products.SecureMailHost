"""
$Id: common.py,v 1.1 2005/02/28 05:10:38 limi Exp $
"""

from Testing import ZopeTestCase

ZopeTestCase.installProduct('generator')
ZopeTestCase.installProduct('validation')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')

ZopeTestCase.installProduct('PloneSoftwareCenter')

from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase
from Products.Archetypes.tests.utils import makeContent

from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

def populate(portal, pkg='plone', release='2.0',
             filename='plone-2.0.tgz'):
    psc = makeContent(portal, portal_type='PloneSoftwareCenter', id='psc')
    #if pkg in portal.objectIds():
    #    package = portal[pkg]
    #else:
    package = makeContent(psc, portal_type='PSCProject', id=pkg)
    #releasef = makeContent(package, portal_type='PSCReleaseFolder', id='releases')
    releasef = package.releases
    release = makeContent(releasef, portal_type='PSCRelease', id=release)
    file = makeContent(release, portal_type='PSCFile', id=filename)
    return package, releasef, release, file

def new_release(release_folder, new_id):
    return makeContent(release_folder, portal_type='PSCRelease', id=new_id)
