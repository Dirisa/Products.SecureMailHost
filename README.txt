PloneLocalFolderNG

    PloneLocalFolderNG is a Plone2-only product to mount a local filesystem as
    a folder into a Plone site.

Requirements:

    Archetypes 1.2+
    TextIndexNG2 2.0.6 (for optional catalog text-indexing of local filesystem contents)
    various system utilities for optional MD5 checksum generation; unzip'ing; text harvesting
      from file formats such as pdf's, MS Word/Powerpoint/Excel files, etc.

Install:

    Use the CMFQuickinstaller tool in the ZMI or "Add/Remove Products" from
    the Plone setup menu. Then, add PloneLocalFolderNG object(s) via non-ZMI web interface.
    
    Optional features such MD5-based checksum verification of file uploads, verification
    and unpacking of zip'd files, and TextIndexNG2-based catalog text indexing of 
    PloneLocalFolderNG file contents require installation of additional system utilities.
    (specific documentation for this to follow as time permits!)

Author:

    (C) by Andreas Jung, D-72070 Tübingen, Germany

License:

    Published under the Zope Public License ZPL

