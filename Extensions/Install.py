# installation used by quickinstaller

from Products.Archetypes import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.PloneFormMailer import PROJECTNAME, GLOBALS

from StringIO import StringIO

def install(self):
    out = StringIO()
    classes=listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)


    return out.getvalue()
