"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: CollectorTool.py,v 1.1 2004/10/10 14:26:09 ajung Exp $
"""


from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import View
from OFS.SimpleItem import SimpleItem

from config import CollectorTool
import util

class CollectorTool(SimpleItem):
    """ A tool to provide common functionalities """

    id = CollectorTool
    security = ClassSecurityInfo()

    security.declareProtected(View, 'getTrackerUsers')
    def getTrackerUsers(self, staff_only=0, unassigned_only=0, with_groups=0):
        """ return a list of dicts where every item of the list
            represents a user and the dict contain the necessary
            informations for the presentation.
        """

        membership_tool = getToolByName(self, 'portal_membership', None)
        collector = self.aq_parent

        staff = []
        users = collector.getUsers()
        for role in ('manager', 'supporter', 'reporter'):
            staff.extend(users.getUsersForRole(role))

        all_names = []
        folder = self
        running = 1
        while running:     # search for acl_users folders
            if hasattr(folder, 'acl_users'):
                usernames = folder.acl_users.getUserNames()
                for name in usernames:
                    if not name in all_names:
                        all_names.append(name)

            if len(folder.getPhysicalPath()) == 1:
                running = 0
            folder = folder.aq_parent

        # Filter out non-existing users
        staff = [s for s in staff if s in all_names]

        if staff_only:
            names = staff
        else:
            names = all_names + staff

        l = []
        groups = self.pcng_get_groups()  # get group IDs from GRUF

        reporters = users.getUsersForRole('reporter')
        managers = users.getUsersForRole('manager')
        supporters = users.getUsersForRole('supporter')

        for name in util.remove_dupes(names):
            if name.replace('group_', '') in groups and not with_groups: continue  # no group names !!!
            member = membership_tool.getMemberById(name)
            d = { 'username':name, 'role':'', 'fullname':'', 'email':''}

            if member:
                d['fullname'] = member.getProperty('fullname')
                d['email'] = member.getProperty('email')

            if name in reporters: d['role'] = 'Reporter'
            if name in supporters: d['role'] = 'Supporter'
            if name in managers: d['role'] = 'TrackerAdmin'
            l.append(d)

        l.sort(lambda a,b: cmp(a['username'].lower(), b['username'].lower()))

        if staff_only:
            return [item for item in l if item['username'] in staff]
        elif unassigned_only:
            return [item for item in l if item['username'] not in staff]
        else:
            return l

InitializeClass(CollectorTool)
