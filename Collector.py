from Products.Archetypes.public import BaseSchema, Schema, DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import BaseFolder, registerType
from Products.BTreeFolder2 import CMFBTreeFolder

from Products.CMFCore import CMFCorePermissions

VOC_LIMIT_FOLLOWUPS = DisplayList((
  (1, 'Yes'),
  (0, 'No'),
))

schema = BaseSchema +  Schema((
    StringField('description',
                searchable=1,
                ),
    StringField('limit_followups',
                vocabulary=VOC_LIMIT_FOLLOWUPS,
                widget=SelectionWidget,
                ),
    StringField('collector_email',
                searchable=0,
                ),
    ))

class Collector(BaseFolder):
    """This is a sample Collector, it has an overridden view for show,
    but this is purely optional
    """

    schema = schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'collector_view',
        'permissions': (CMFCorePermissions.View,)
        },)


registerType(Collector)
