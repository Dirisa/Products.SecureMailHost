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
      generation. So far, this product has only been tested with the following 
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

Author:

    (C) by Andreas Jung, D-72070 Tübingen, Germany
    
Maintainer:

    Since v0.4, Mike Garnsey (sourceforge id 'mgarnsey') is maintaining this product.

License:

    Published under the Zope Public License ZPL

