from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.TextIndexNG2.TextIndexNG import manage_addTextIndexNG
from Products.PloneLocalFolderNG import PloneLocalFolderNG
from App.FindHomes import SOFTWARE_HOME,INSTANCE_HOME
import os
#from os.path import join
#import string

UID_CATALOG = 'testZcat'
UID_INDEX = 'SearchableText'
ID_INDEX  = 'id'
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
		out.write("\nfound: '%s' ZCatalog\n" % UID_CATALOG)
	else:
		#out.write('\n %s NOT found!!!' % UID_CATALOG)
		manage_addZCatalog(portal,UID_CATALOG,None)
		out.write("\nadded: '%s' ZCatalog\n" % UID_CATALOG)

	testCatalogObj = getattr( portal, UID_CATALOG )

	extra = arguments(use_stopwords=None, use_converters=1, truncate_left=1)

	try:
		manage_addTextIndexNG(testCatalogObj, UID_INDEX, extra)
		out.write("\nadded: '%s' index\n" % UID_INDEX)
	except:
		out.write("\nfound: '%s' Index\n" % UID_INDEX)
		pass

	try:
		testCatalogObj.manage_addIndex(ID_INDEX, 'FieldIndex')
		out.write("\nadded: '%s' index\n" % ID_INDEX)
	except:
		out.write("\nfound: '%s' Index\n" % ID_INDEX)
		pass

	#out.write('\n indices = %s' % testCatalogObj.Indexes['xSearchableText'].__class__.__name__)

	catalogTool = getToolByName(portal, UID_CATALOG)
	#out.write("\ncatalogTool: %s" % catalogTool)

	if hasattr(portal, UID_PLFNG_TEST):
	   out.write("\nfound: '%s' PLFNG instance\n" % UID_PLFNG_TEST )
	   newObj = getattr( portal, UID_PLFNG_TEST )
	else:
		# locate FS path to SamplesFiles subdir in INSTANCE_HOME or SOFTWARE_HOME

		FSpath = os.path.join(INSTANCE_HOME,'Products','PloneLocalFolderNG','tests','SamplesFiles')+os.path.sep
		if os.path.exists(FSpath):
			out.write( "\nfound: 'SamplesFiles' subdir in INSTANCE_HOME\n" )
		else:
			FSpath = os.path.join(SOFTWARE_HOME,'Products','PloneLocalFolderNG','tests','SamplesFiles')+os.path.sep
			if os.path.exists(FSpath):
				out.write( "\nfound: 'SamplesFiles' subdir in SOFTWARE_HOME\n" )
			else:
				out.write( "\nERROR!!! could not find 'SamplesFiles' subdir to proxy for a test PLFNG instance.\n\n  Test aborted.\n" )
				return out.getvalue()

		portal.invokeFactory(id=UID_PLFNG_TEST, type_name='PloneLocalFolderNG')
		newObj = getattr( portal, UID_PLFNG_TEST )
		newObj.title = UID_PLFNG_TEST
		newObj.folder = FSpath
		newObj.require_MD5_with_upload = 1
		newObj.generate_MD5_after_upload = 1
		newObj.quota_aware = 0
		newObj.allow_file_unpacking = 1
		out.write( "\nadded: '%s' PLFNG instance.\n" % UID_PLFNG_TEST )

	out.write("\nCatalog INDEX test:\n")
	filesCataloged = newObj.catalogContents(rel_dir=None, catalog=UID_CATALOG)
	out.write("\n   Cataloged %d files\n" % filesCataloged)

	out.write("\nCatalog SEARCH test:\n")
	out.write("\n   Searching 'HTMLTEXT'...")
	# get catalog search results fopr text 'Spain'
	results = testCatalogObj.searchResults(SearchableText='HTMLTEXT')
	results_length = len(results)
	out.write("found %d results\n\n" % results_length)
	
	# the following isnt working yet....
	
	# get Object of the first returned HTMLTEXT
	#if results_length>=0: obj=results[0].getObject()
	#else: obj=None
	#if results_length==1 and obj and obj.id=='sample.html':
	#   out.write("passed")
	#else:
	#   if results_length>1:
	#      out.write("FAILED. Found %d results instead of 1" % results_length)
	#   elif results_length==0:
	#      out.write("FAILED. Not found any result.")
	#   else:
	#      out.write("FAILED. Expected is 'sample.html' but returned is: %s" % obj.id)

	return out.getvalue()

