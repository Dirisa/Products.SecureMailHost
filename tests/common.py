from Testing import ZopeTestCase

from Products.PloneClipboard.config import *
from Products.PloneClipboard.Extensions.Install import install

from Products.Archetypes.Extensions.Install import install as installAT

def installProducts():
    ZopeTestCase.installProduct('Archetypes')
    ZopeTestCase.installProduct('PortalTransforms')    
    ZopeTestCase.installProduct('ReferenceFolder')
    ZopeTestCase.installProduct(PROJECTNAME)

def installWithinPortal(portal):
    installAT(portal, include_demo=1)
    install(portal)
