"""
$Id: utils.py,v 1.1 2005/02/28 05:10:36 limi Exp $
"""

from Products.Archetypes.utils import findDict
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from os.path import join, abspath, dirname, basename

PREFIX = abspath(dirname(__file__))

def data_file_path(file):
    return join(PREFIX, 'content', 'data', file)

def setSchemata(klass, name='default', fields=None):
    schema = klass.schema.copy()
    if fields is not None:
        fields = [f for f in schema.fields() if f.getName() in fields]
    else:
        fields = schema.fields()
    for f in fields:
        if name != 'metadata':
            f.isMetadata = 0
        f.schemata = name

    klass.schema = schema

def std_modify_fti(fti, allowed = (), global_allow=0):
    refs = findDict(fti['actions'], 'id', 'references')
    refs['visible'] = 0
    refs = findDict(fti['actions'], 'id', 'metadata')
    refs['visible'] = 0
    fti['global_allow'] = global_allow

def folder_modify_fti(fti, allowed = (), global_allow=0):
    std_modify_fti(fti, allowed)
    fti['filter_content_types'] = 1
    fti['global_allow'] = global_allow
    fti['allowed_content_types'] = allowed
    for a in fti['actions']:
        a['category'] = 'folder'

def changeWidgetLabel(klass, field_name, new_value):
    # convenient wrapper for the lazy
    changeWidgetThing(klass, field_name, "label", new_value)

def changeWidgetThing(klass, field_name, key, value):
    schema = klass.schema.copy()
    setattr(schema[field_name].widget, key, value)
    klass.schema = schema
