"""
##############################################################################
#
# Copyright (c) 2003 struktur AG and Contributors. # All Rights Reserved.
# # This software is subject to the provisions of the Zope Public License,# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# $Id: __init__.py,v 1.3 2003/12/10 00:04:06 longsleep Exp $ (Author: $Author: longsleep $)
"""


from AccessControl import ModuleSecurityInfo
from Globals import InitializeClass
import Products.CMFCore.utils
import catalogawarehook

ADD_CONTENT_PREMISSIONS = 'Manage Portal'
lang_globals = globals()

PKG_NAME = "CMFSquidTool"

from Products.CMFSquidTool.SquidTool import SquidTool
tools = (SquidTool,)

def initialize(context):
    Products.CMFCore.utils.ToolInit("Squid Tool", tools=tools,
                   product_name=PKG_NAME,
                   icon="tool.gif",
                   ).initialize(context)

types_globals=globals()
