from Products.Archetypes.public import BaseSchema, Schema, DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget

schema = BaseSchema +  Schema((
    StringField('description',
                searchable=1,
                ),
    StringField('progress_hours_estimated',
                searchable=1,
                schemata='progress'
                ),
    StringField('progress_hours_needed',
                searchable=1,
                schemata='progress'
                ),
    StringField('progress_percent_done',
                searchable=1,
                schemata='progress'
                ),
    StringField('contact_name',
                searchable=1,
                schemata='contact'
                ),
    StringField('contact_address',
                searchable=1,
                schemata='contact'
                ),
    StringField('contact_email',
                searchable=1,
                schemata='contact'
                ),
    StringField('contact_phone',
                searchable=1,
                schemata='contact'
                ),
    StringField('contact_fax',
                searchable=1,
                schemata='contact'
                ),
    ))
