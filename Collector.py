
from Globals import InitializeClass
from AccessControl import getSecurityManager, ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CatalogTool import CatalogTool

from Products.BTreeFolder2 import CMFBTreeFolder
from Products.Archetypes.public import BaseFolder, registerType

from Transcript import Transcript, TranscriptEntry
from config import ManageCollector
import util
import collector_schema

class Collector(BaseFolder):
    """ PloneCollectorNG """

    schema = collector_schema.schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'pcng_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'history',
        'name': 'History',
        'action': 'pcng_history',
        'permissions': (ManageCollector,)
        },
        {'id': 'staff',
        'name': 'Staff',
        'action': 'pcng_staff',
        'permissions': (ManageCollector,)
        },
        {'id': 'issueproperties',
        'name': 'Issue properties',
        'action': 'pcng_issue_properties',
        'permissions': (ManageCollector,)
        },
        {'id': 'notifications',
        'name': 'Notifications',
        'action': 'pcng_notifications',
        'permissions': (ManageCollector,)
        },
        )

    __ac_roles__ = ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter')
    security = ClassSecurityInfo()

    def __init__(self, oid, **kwargs):
        BaseFolder.__init__(self, oid, **kwargs)
        self._supporters = self._admins = self._reporters = []
        self.transcript = Transcript()
        self._setup_collector_catalog()
        self.transcript.addComment('Tracker created')

        # setup roles 
        username = util.getUserName()
        for role in ('Manager', 'TrackerAdmin', 'Owner'):
            util.add_local_role(self, username, role)

    def _setup_collector_catalog(self):
        """Create and situate properly configured collector catalog."""
        catalog = PloneCollectorNGCatalog()
        self._setObject(catalog.id, catalog)
        catalog = catalog.__of__(self)

    def pre_validate(self, REQUEST, errors):
        """ Hook to perform pre-validation actions. We use this
            hook to log changed properties to the transcript.
        """

        te = TranscriptEntry()
        for name in REQUEST.form.keys():
            new = REQUEST.get(name, None)
            old = getattr(self, name, None)
            if old:
                if old != new:
                    te.addChange(name, old, new)

        self.transcript.add(te)
        self.transcript._p_changed = 1

    ######################################################################
    # Staff handling
    ######################################################################

    security.declareProtected(ManageCollector, 'set_staff')
    def set_staff(self, reporters=[], admins=[], supporters=[], RESPONSE=None):
        """ set the staff """

        self._reporters = reporters
        self._admins = admins
        self._supporters = supporters
    
    security.declareProtected(ManageCollector, 'getSupporters')
    def getSupporters(self): return self._supporters

    security.declareProtected(ManageCollector, 'getAdmins')
    def getAdmins(self): return self._admins

    security.declareProtected(ManageCollector, 'getReporters')
    def getReporters(self): return self._reporters
        


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
