
from Globals import InitializeClass
from AccessControl import getSecurityManager
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CatalogTool import CatalogTool

from Products.Archetypes.public import BaseSchema, Schema, DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import BaseFolder, registerType
from Products.BTreeFolder2 import CMFBTreeFolder

from Transcript import Transcript, TranscriptEntry

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
        'action': 'pcng_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'history',
        'name': 'History',
        'action': 'pcng_history',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'staff',
        'name': 'Staff',
        'action': 'pcng_staff',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'issueproperties',
        'name': 'Issue properties',
        'action': 'pcng_issue_properties',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'notifications',
        'name': 'Notifications',
        'action': 'pcng_notifications',
        'permissions': (CMFCorePermissions.View,)
        },
        )

    def __init__(self, oid, **kwargs):
        BaseFolder.__init__(self, oid, **kwargs)
        self.transcript = Transcript()
        self._setup_collector_catalog()
        self.transcript.addComment('Tracker created')
        
    def _setup_collector_catalog(self):
        """Create and situate properly configured collector catalog."""
        catalog = PloneCollectorNGCatalog()
        self._setObject(catalog.id, catalog)
        catalog = catalog.__of__(self)


registerType(Collector)


class PloneCollectorNGCatalog(CatalogTool):
    """ catalog for collector issues """

    id = 'pcng_catalog'
    meta_type = 'PloneCollectorNG Catalog'
    portal_type = 'PloneCollectorNG Catalog'

    def enumerateIndexes(self):
        standard = CatalogTool.enumerateIndexes(self)
        custom = (('status', 'FieldIndex'),
                  ('topic', 'FieldIndex'),
                  ('subtopic', 'FieldIndex'),
                  ('classification', 'FieldIndex'),
                  ('importance', 'FieldIndex'),
                  ('security_related', 'FieldIndex'),
                  ('confidential', 'FieldIndex'),
                  ('submitter_id', 'FieldIndex'),
                  ('submitter_email', 'FieldIndex'),
                  ('version_info', 'TextIndex'),
                  ('assigned_to', 'KeywordIndex'),
                  ('deadline', 'FieldIndex'),
                  ('progress', 'FieldIndex'),
                  ('getId', 'FieldIndex'),
                  )
        custom = tuple([col for col in custom if col not in standard])
        return standard + custom

    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""
        standard = CatalogTool.enumerateColumns(self)
        custom = ('id', 'status', 'submitter_id', 'topic', 'subtopic', 'classification',
                  'importance', 'security_related', 'confidential', 'version_info',
                  'assigned_to', 'deadline', 'progress', 'getId',
                  )
        custom = tuple([col for col in custom if col not in standard])
        return standard + custom

InitializeClass(PloneCollectorNGCatalog)
