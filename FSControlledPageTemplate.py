##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##########################################################################
""" Customizable validated page templates that come from the filesystem.

$Id: FSControlledPageTemplate.py,v 1.4 2003/09/12 22:49:03 tesdal Exp $
"""

import Globals, Acquisition
from AccessControl import ClassSecurityInfo
from OFS.Cache import Cacheable
from Products.PageTemplates.ZopePageTemplate import Src
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import expandpath
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.FSPageTemplate import FSPageTemplate as BaseClass
from ControlledPageTemplate import ControlledPageTemplate
from ControlledBase import ControlledBase
from BaseControlledPageTemplate import BaseControlledPageTemplate
from utils import logException


class FSControlledPageTemplate(BaseClass, BaseControlledPageTemplate):
    """Wrapper for Controlled Page Template"""
     
    meta_type = 'Filesystem Controlled Page Template'

    manage_options=(
        ({'label':'Customize', 'action':'manage_main'},
         {'label':'Test', 'action':'ZScriptHTML_tryForm'},
         {'label':'Validation','action':'manage_formValidatorsForm'},
         {'label':'Actions','action':'manage_formActionsForm'},
        ) + Cacheable.manage_options)

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)


    def __init__(self, id, filepath, fullname=None, properties=None):
        BaseClass.__init__(self, id, filepath, fullname, properties)
        self.filepath = filepath
        self._read_action_metadata(self.getId(), filepath)
        self._read_validator_metadata(self.getId(), filepath)


    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, object, container):
        try:
            BaseClass.manage_afterAdd(self, object, container)
            # Re-read .metadata after adding so that we can do validation checks
            # using information in portal_form_controller.  Since manage_afterAdd
            # is not guaranteed to run, we also call these in __init__
            self._read_action_metadata(self.getId(), self.filepath)
            self._read_validator_metadata(self.getId(), self.filepath)
        except:
            logException()
            raise


    def __call__(self, *args, **kwargs):
        return self._call(FSControlledPageTemplate.inheritedAttribute('__call__'), *args, **kwargs)


    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ControlledPageTemplate(self.getId(), self._text, self.content_type)
        obj.expand = 0
        obj.write(self.read())
        return obj


    security.declarePublic('writableDefaults')
    def writableDefaults(self):
        """Can default actions and validators be modified?"""
        return 0


d = FSControlledPageTemplate.__dict__
d['source.xml'] = d['source.html'] = Src()

Globals.InitializeClass(FSControlledPageTemplate)

registerFileExtension('cpt', FSControlledPageTemplate)
registerMetaType('Controlled Page Template', FSControlledPageTemplate)