PloneLocalFolderNG

    PloneLocalFolderNG is a Plone2-only product to mount a local filesystem as
    a folder into a Plone site.

Requirements:

    Archetypes 1.2+
    
    (optional) TextIndexNG2 (http://www.zope.org/Members/ajung/TextIndexNG)
     and associated system utilites for optional zCatalog text-indexing of 
     local filesystem contents.  For example, with converters like pdftotext, 
     pptHtml, and vwWare, PDF MSPowerpoint, and MSWord files can be text indexed.
     TextIndexNG2 has built-in support for text indexing plain, html, sgml, & xml
     file types).  See DEPENDENCIES.txt for more information.
     
    (optional) System utilities for optional file unzip'ing and MD5 checksum
      generation. Note: python provides built-in support for both md5 generation
      and unzip functionality, and the official 0.60 release of PLNFG will 
      not require these external utilities.  FYI, native python MD5 support 
      has already been added to the CVS baseline, with now optional support for
      external MD5 system utilities (mainly because the glue code was already
      written for it!, but possibly for performance reasons).  Speaking of 
      performance, for small files, my informal benchmarking shows
      that the python md5 module is approx 2x faster than the md5deep utility.
      Rock on, python team!!!!  For medium-sized files (~100MB), performance 
      for both was about the same. For larger files (550MB was the only one I 
      tested), md5deep was about 30% faster.
      
      So far, this product has only been tested with the following 
      utilities:
        - unzip/zipinfo: UnZip v5.50 by Info-ZIP (http://www.info-zip.org/) 
        - md5: md5deep v1.2 (http://md5deep.sourceforge.net/)
      
      See DEPENDENCIES.txt for more information.
      
    (optional) mxmCounter (http://www.mxm.dk/products/public/mxmCounter)
     mxmCounter is a nice little hit counter, and I put hooks into PLFNG's 
     showFile() to use mxmCounter if its installed.  Note: for this to 
     work with mxmCounter (v1.1.0), you will need to modify/extend the 
     mxmCounter class by adding the following method (I have contacted the
     mxmCounter author to ask that this type of functionality be added to 
     the baseline of mxmCounter):

		def proxyObject_increase_count(self,url_path): 
			return increase_count(url_path, self.save_interval)
   

Install:

    Use the CMFQuickinstaller tool in the ZMI or "Add/Remove Products" from
    the Plone setup menu. Then, add PloneLocalFolderNG object(s) via 
    ***non-ZMI*** web interface. 
    
    Optional features such MD5-based checksum verification of file uploads, 
    verification and unpacking of zip'd files, and TextIndexNG2-based catalog
    text indexing of PloneLocalFolderNG file contents require installation of
    additional system utilities. See DEPENDENCIES.txt for more information.
    
    Configuration notes on the optional PLFNG cataloging action capability:
    (This is a rough outline of the recipe that I have used to get
     PLFNG-based files text-indexed into Plone's portal_catalog.  
     You ***MUST*** have the TextIndexNG2 product successfully working
     before the PLFNG catalog action will work!)
     
	    1. using ZMI, traverse to the 'portal_catalog'

		 2. select the 'Indexes' tab

	    3. delete the Index 'SearchableText' (type=ZCTextIndex)

		 4. add a 'TextIndexNG2' with defaults except:
    
	    		Id = 'SearchableText' 
  		  		Left truncation = enabled
    			Document Converters = enabled

		 5. to test, go to one of your PLFNG instances
          (preferrably pointing to a folder without
           thousands of files in it....but with
           representative file types in it)

       6. click the catalog tab of the PLFNG object

		 7. click on the 'Catalog Contents' button

		 8. view results of the PLFNG catalog operation 
		   (on my box, if 'average index rate' is 
		   10^5 KB/sec, it finished too quickly, meaning
		   that the something is not right with the
		   config of TextIndexNG2 --ie, it didnt do
		   text extraction of the PLFNG files)

		 9. using ZMI, traverse to the 'portal_catalog'
 		    and click the 'Catalog' tab. 

		10. look for Object Identifier(s) matching the
		    PLFNG files you just cataloged, Note, 
		    Object type will be 'FileProxy', and only
		    20 entries are listed per page, so don't 
		    freak out if you don't see your newly 
		    cataloged items on the 1st page ;)
		
		11. click on one of your newly cataloged items
		    to bring up its catalog record, and study
		    the 'SearchableText' key in the Index Contents
		    section.  It should contain a list of the text
		    words from the cataloged file

    
    For those who have TextIndexNG2 successfully running, there is now a
    an initial but primative unit testing implementation of the catalog 
    action.  To use it, create an external method as follows:

		id = PLFNG_catalogUnitTest (or whatever you want to call it)
		Module Name = PloneLocalFolderNG.testPLFNGContentsCataloging
		Function Name = PLFNGCatalogTest

	 when you run it (by clicking the test tab), it will create a 
	 'testZcat' ZCatalog along with a PLFNG instance 'testPLFNG' 
	 (pathed to the SamplesFiles subfolder of the PLFNG tests folder)
	  and then catalog these files.
	  
	  


Author:

    (C) by Andreas Jung, D-72070 Tübingen, Germany
    
Maintainer:

    Since v0.4, Mike Garnsey (sourceforge id 'mgarnsey') is maintaining this product.

License:

    Published under the Zope Public License ZPL

