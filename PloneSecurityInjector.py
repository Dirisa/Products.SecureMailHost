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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *

from Products.CMFPlone.WorkflowTool import WorkflowTool 
##code-section module-header #fill in your manual code here
##/code-section module-header


from string import split
from zExceptions import Unauthorized

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import CMFCorePermissions
from Products.PloneSecurityInjector.interfaces.PloneSecurityInjector import IPloneSecurityInjector

try:
    from Products.TeamSpace.interfaces.security import ITeamSecurity
except:
    ITeamSecurity=None
    #No teamSpace installed

class PloneSecurityInjector(UniqueObject,WorkflowTool,BaseFolder):
    security = ClassSecurityInfo()
    portal_type = meta_type = 'PloneSecurityInjector' 
    archetype_name = 'PloneSecurityInjector'   #this name appears in the 'add' box 
    allowed_content_types = [] 
    id = 'portal_securityinjector'
    ##code-section class-header #fill in your manual code here
    ##/code-section class-header
    __implements__ = (IPloneSecurityInjector)

    schema=BaseSchema  + Schema((),)

    # tool-constructors have no id argument, the id is fixed
    def __init__(self):
        BaseFolder.__init__(self,'portal_securityinjector')
        self._md={}
        
        ##code-section constructor-footer #fill in your manual code here
        ##/code-section constructor-footer

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_get_breakpoint')
    def manage_get_breakpoint(self,obj):
        wf=self.portal_securityinjector.securityinjector_workflow
        if wf.getReviewStateOf(obj)=='aqbreakyes':
            return 1
        else:
            return 0
        
    security.declareProtected(CMFCorePermissions.ManagePortal, 'getWorkflowsFor')
    def getWorkflowFor(self,ob):
        """Return Workflow for object"""
        return self.getChainFor(ob)

    security.declarePrivate('check_local_roles')        
    def check_local_roles(self,user,aq_breakpoint):
        local_roles=aq_breakpoint.get_local_roles()
        member_roles=self.sort_member_to_roles(local_roles)
        if user.id in member_roles.keys() or user.has_role('Manager'):
            return 1
        else:
            raise Unauthorized
        
    security.declarePrivate('check_security')        
    def check_security(self,request,user):
        wf=self.portal_securityinjector.securityinjector_workflow
        folder=self.portal_url.getPortalObject()
        #is there a better way to get the url wich is requested?
        surl = split(request['URL0'][len(self.portal_url())+1:],'/')
        aq_breakpoint=None
        #We only will check Objects wich are avaliable addable objects in
        #Plone the rest is validated from the old security so that here is
        #no security hole!! This not validate stuff are mostly images,css,java
        #script stuff and file system files.
        if surl and surl[0] in folder.objectIds():
            for item in surl:
                #There would be no aq_breakpoint at root folder so first step
                #in the next folder befor testing
                folder=folder.restrictedTraverse(item)
                if folder.isPrincipiaFolderish and wf.getReviewStateOf(folder)=='aqbreakyes':
                    aq_breakpoint=folder
                else:
                    #If traversal item is not longer a folder we can break here.
                    #Perhaps in future it will make sens to add this feature also to
                    #non folderish object but at this time it's not usefull
                    pass
            if aq_breakpoint:
                #If we have a aq_breakpoint we have to check if there is
                #a definition of local membership to this folder. This can be over
                #local role or team membership.
                if ITeamSecurity and ITeamSecurity.isImplementedBy(aq_breakpoint):
                    teams=aq_breakpoint._getTeamsForLocalRoles()
                    memberships = [team.getMembershipByMemberId(user.id) for team in teams if team.getMembershipByMemberId(user.id)]
                    if memberships:
                        return 1
                    else:
                        if self.check_local_roles(user,aq_breakpoint):
                            return 1
                else:
                    if self.check_local_roles(user,aq_breakpoint):
                        return 1
            else:
                return 1
        else:
            pass

    security.declarePrivate('append_roles')
    def append_roles(self,local_roles,roles):
        for role in local_roles:
            if role not in roles:
                roles.append(role)

    security.declarePrivate('sort_member_to_roles')        
    def sort_member_to_roles(self,local_roles):
        """Ok here we only need the meber and his roles he has {user.id:[Role1,Role2,...]}"""
        member_roles={}
        groups=self.portal_groups.listGroupIds()
        members=self.portal_membership.listMemberIds()
        
        for local_role in local_roles:
            if local_role[0].startswith('group_'):
                members=self.get_all_group_members(local_role[0])
                if members:
                    for member in members:
                        if member_roles.get(member,None):
                            self.append_roles(local_role[1],member_roles[member])
                        else:
                            member_roles[member]=[]
                            self.append_roles(local_role[1],member_roles[member])
            else:                
                if member_roles.get(local_role[0],None):
                    self.append_roles(local_role[1],member_roles[local_role[0]])
                else:
                    member_roles[local_role[0]]=[]
                    self.append_roles(local_role[1],member_roles[local_role[0]])
                        
        return member_roles
                
    security.declarePrivate('get_all_group_members')
    def get_all_group_members(self,group):
        """Get all members of a group not local roles, Searching for given Group id"""
        mtool=self.portal_membership
        members=mtool.listMemberIds()
        results=[]
        for member in members:
            if group in mtool.getMemberById(member).getGroups():
                    results.append(member)
        return results


    #Methods


    # uncomment lines below when you need
    factory_type_information={
        'allowed_content_types':allowed_content_types,
        'allow_discussion': 0,
        #'content_icon':'PloneSecurityInjector.gif',
        'immediate_view':'base_view',
        'global_allow':0,
        'filter_content_types':1,
        }

registerType(PloneSecurityInjector)
# end of class PloneSecurityInjector

##code-section module-footer #fill in your manual code here
##/code-section module-footer


