from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.TextIndexNG2.TextIndexNG import manage_addTextIndexNG
from Products.PloneLocalFolderNG import PloneLocalFolderNG
from App.FindHomes import SOFTWARE_HOME
import os
#from os.path import join
#import string

UID_CATALOG = 'testZcat'
UID_INDEX = 'SearchableText'
UID_PLFNG_TEST = 'testPLFNG'


class arguments: 

    def __init__(self, *args, **kw):
        self._keys = []

        for k,v in kw.items():
            setattr(self,k,v)
            self._keys.append(k)

    def keys(self): return self._keys



def PLFNGCatalogTest(self):	
	out=StringIO()
	
	portal = getToolByName(self, 'portal_url').getPortalObject()
	
	# create the test ZCatalog as necessary
	if hasattr(portal, UID_CATALOG):
		out.write("\nfound: '%s' ZCatalog" % UID_CATALOG)
	else:
		#out.write('\n %s NOT found!!!' % UID_CATALOG)
		manage_addZCatalog(portal,UID_CATALOG,None)
		out.write("\nadded: '%s' ZCatalog" % UID_CATALOG)
	
	testCatalogObj = getattr( portal, UID_CATALOG )

	extra = arguments(use_stopwords=None, use_converters=1, truncate_left=1)
	
	try:
		manage_addTextIndexNG(testCatalogObj, UID_INDEX, extra)
		out.write("\nadded: '%s' index" % UID_INDEX)
	except:
		out.write("\nfound: '%s' Index" % UID_INDEX)
		pass	

	#out.write('\n indices = %s' % testCatalogObj.Indexes['xSearchableText'].__class__.__name__)
	
	catalogTool = getToolByName(portal, UID_CATALOG)
	#out.write("\ncatalogTool: %s" % catalogTool)
	
	if hasattr(portal, UID_PLFNG_TEST):
	   out.write( '-!- %s already exists....leaving it alone.\n' % id )
	   newObj = getattr( portal, UID_PLFNG_TEST )
	else:
		FSpath = os.path.join(SOFTWARE_HOME,'Products')
		FSpath = os.path.join(FSpath,'PloneLocalFolderNG')
		FSpath = os.path.join(FSpath,'tests')
		FSpath = os.path.join(FSpath,'SamplesFiles')+os.path.sep

		portal.invokeFactory(id=UID_PLFNG_TEST, type_name='PloneLocalFolderNG')
		newObj = getattr( portal, UID_PLFNG_TEST )
		newObj.title = UID_PLFNG_TEST
		newObj.folder = FSpath
		newObj.require_MD5_with_upload = 1
		newObj.generate_MD5_after_upload = 1
		newObj.quota_aware = 0
		newObj.allow_file_unpacking = 1
		out.write( "\nadded: '%s' PLFNG instance.\n" % UID_PLFNG_TEST )
		
	filesCataloged, filesNotCataloged = newObj.catalogContents(rel_dir=None, catalog=UID_CATALOG)
	out.write("\nfilesCataloged=%d , filesNotCataloged = %d" % (filesCataloged,filesNotCataloged))	
		
	return out.getvalue()
	
def macPathTest(self):	
	out=StringIO()
	return out.getvalue()
	
		