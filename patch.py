# File: PloneSecurityInjector.py

# Copyright (c) 2004 by tomcom GmbH
#
# Generated: Tue Aug 03 15:01:56 2004
# Generator: ArchGenXML Version 1.1 beta 1 http://sf.net/projects/archetypes/
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = 'Kai Hoppert <kai.hoppert@tomcom.de>'
__docformat__ = 'plaintext'

import Zope
import Globals
from zExceptions import Unauthorized
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from Products.CMFCore.utils import getToolByName
from string import split

def validated_hook(request, user):
    newSecurityManager(request, user)
    version = request.get(Globals.VersionNameName, '')
    findPloneSite(request,user)
    if version:
        object = user.aq_parent
        if not getSecurityManager().checkPermission(
            'Join/leave Versions', object):
            request['RESPONSE'].setCookie(
                Globals.VersionNameName,'No longer active',
                expires="Mon, 25-Jan-1999 23:59:59 GMT",
                path=(request['BASEPATH1'] or '/'),
                )
            Zope.DB.removeVersionPool(version)
            raise Unauthorized, "You don't have permission to enter versions."

def findPloneSite(request,user):
    #First find root or application instance
    try:
        ploneSite=getToolByName(user,'portal_url').getPortalObject()
    except AttributeError:
        #This is no Plone site. Anything else so we exit here
        return 0
    #If _isPortalRoot  then it's a Plone Portal and not Zope root.
    #We have to test this here because a user can also exists in Zope acl_users
    #and not in Plone acl_users
    if hasattr(ploneSite,'_isPortalRoot'):
        sitool=getToolByName(ploneSite,'portal_securityinjector',None)
        if sitool:
            sitool.check_security(request,user)

#Hook the validation hook. Can anybody tell me how to doo this clean.
#I tried and searched but found nothing :(
print '*** Patching validated_hook from Zope.App.startup'
Zope.App.startup.validated_hook=validated_hook
