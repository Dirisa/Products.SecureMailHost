"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: issue_schema.py,v 1.7 2003/09/13 11:37:39 ajung Exp $
"""

from OrderedSchema import OrderedSchema 
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, IdWidget, StringWidget

schema = OrderedSchema((
    StringField('id',
                required=1,
                mode="rw",
                accessor="getId",
                mutator="setId",
                default=None,
                schemata='default',
                widget=IdWidget(label_msgid="label_name",
                                description_msgid="help_name",
                                i18n_domain="plone"),
                ),
    StringField('title',
                required=1,
                searchable=1,
                default='',
                accessor='Title',
                schemata='issuedata',
                widget=StringWidget(label_msgid="label_title",
                                    description_msgid="help_title",
                                    i18n_domain="plone"),
                ),
    StringField('description',
                searchable=1,
                schemata='issuedata'
                ),
    StringField('solution',
                searchable=1,
                schemata='issuedata'
                ),
    StringField('progress_hours_estimated',
                schemata='progress'
                ),
    StringField('progress_hours_needed',
                schemata='progress'
                ),
    StringField('progress_percent_done',
                schemata='progress'
                ),
    # do not remove 'contact_name'
    StringField('contact_name',
                searchable=1,
                required=1,
                schemata='contact'
                ),
    # do not remove 'contact_email'
    StringField('contact_email',
                searchable=1,
                required=1,
                schemata='contact',
                validators=('isEmail',)
                ),
    StringField('contact_address',
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
