"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 Tübingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: Catalog.py,v 1.4 2004/11/12 15:37:46 ajung Exp $
"""


from Globals import InitializeClass 
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.CMFCorePermissions import *

from config import SCHEMA_ID, CollectorCatalog, SEARCHFORM_IGNOREABLE_INDEXES 


try: import Products.TextIndexNG2; txng_version = 2
except ImportError:
    try: import Products.TextIndexNG; txng_version = 1
    except: txng_version = 0


class PloneCollectorNGCatalog(CatalogTool):
    """ catalog for collector issues """

    id = CollectorCatalog
    meta_type = 'PloneCollectorNG Catalog'
    portal_type = 'PloneCollectorNG Catalog'
    security = ClassSecurityInfo()

    def manage_afterAdd(self, container, item):
        """ recreate catalog """

        # We create the indexes and metadata in the manage_afterAdd() hook
        # an *not+ inside the constructor as usually because we need an
        # acquisition context inside enumerateIndexes() to retrieve
        # the issue schema for custom index creation

        self._initIndexes()

    def enumerateIndexes(self):

        if not hasattr(self, 'aq_parent'): return  []   # only through manage_afterAdd()

        custom = [['status', 'FieldIndex'],
                  ['Creator', 'FieldIndex'],
                  ['created', 'DateIndex'],
                  ['last_action', 'DateIndex'],
                  ['SearchableText', 'TextIndex'],
                  ['importance', 'FieldIndex'],
                  ['classification', 'FieldIndex'],
                  ['topic', 'FieldIndex'],
                  ['assigned_to', 'KeywordIndex'],
                  ['progress_deadline', 'FieldIndex'],
                  ['progress_percent_done', 'FieldIndex'],
                  ['getId', 'FieldIndex'],
                  ['numberFollowups', 'FieldIndex'],
                 ]

        # add custom indexes for fields
        custom_keys = [f[0] for f in custom]

        for f in self.aq_parent.atse_getSchemaById(SCHEMA_ID).fields():
            klass = f.__class__.__name__
            widget = f.widget.__class__.__name__
            if getattr(f, 'createindex', 0) == 1 and f.getName() not in custom_keys:
                if klass in ('StringField', 'TextField'):
                    if widget in ('MultiSelectionWidget', 'SelectionWidget'):
                        custom.append( [f.getName(), 'FieldIndex'] )
                    else:
                        custom.append( [f.getName(), 'TextIndex'] )
                elif klass in ('DateTimeField', 'IntField', 'FloatField', 'FixedPointField'):
                    custom.append( [f.getName(), 'FieldIndex'] )
                else:
                    pass

        # Replace TextIndexes with TextIndexNG instances if possible
        for i in range(len(custom)):
            k,v = custom[i]
            if v == 'TextIndex':
                if txng_version == 1: custom[i][1] = 'TextIndexNG'
                if txng_version == 2: custom[i][1] = 'TextIndexNG2'

        return  custom

    def manage_afterClone(self, item):
        self.reindex_issues()

    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""

        if not hasattr(self, 'aq_parent'): return  []  # only through manage_afterAdd()

        custom = ('Description', 'Title', 'Creator', 'created', 'modified',
                  'id', 'status', 'topic', 'classification',
                  'importance', 'assigned_to', 'progress_deadline',
                  'progress_percent_done', 'getId', 'numberFollowups',
                  'last_action', 'numberUploads', 'numberReferences'
                  )
        return custom

    def searchResults(self, REQUEST=None, **kw):
        """ Bypass searchResults() of the CatalogTool """
        return self._catalog.searchResults(*(REQUEST,), **kw)

    __call__ = searchResults


    security.declareProtected(View, 'getIndexes')
    def getIndexes(self):
        """ return a sequence of tuples (indexId, indexType)"""
        return [ (id, idx.meta_type)
                 for id, idx in self._catalog.indexes.items()
                 if not id in SEARCHFORM_IGNOREABLE_INDEXES ]


InitializeClass(PloneCollectorNGCatalog)
