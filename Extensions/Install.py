
"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 T�bingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: Install.py,v 1.4 2004/09/16 17:36:01 ajung Exp $
"""

from cStringIO import StringIO
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.ATSchemaEditorNG.config import GLOBALS, PROJECT_NAME

def install(self):                                       
    out = StringIO()

    install_subskin(self, out, GLOBALS)

    print >> out, "Successfully installed %s." % PROJECT_NAME
    return out.getvalue()
