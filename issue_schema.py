from Products.Archetypes.public import BaseSchema, Schema, DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget
from Products.Archetypes.public import RichWidget

VOC_LIMIT_FOLLOWUPS = DisplayList((
  (1, 'Yes'),
  (0, 'No'),                                       
))

schema = BaseSchema +  Schema((
    StringField('description',
                searchable=1,
                ),
    ))
