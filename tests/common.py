from Testing import ZopeTestCase

from Products.PloneClipboard.config import *
from Products.PloneClipboard.Extensions.Install import install

from Products.Archetypes.Extensions.Install import install as installAT

product_dependencies = ['Archetypes', 'PortalTransforms', 'generator',
                        'validation', 'MimetypesRegistry', 'ReferenceFolder',
                        PROJECTNAME]

def installProducts():
    for product in product_dependencies:
        ZopeTestCase.installProduct(product)

def installWithinPortal(portal):
    installAT(portal, include_demo=1)
    install(portal)
