# Copyright (c) 2003 The Connexions Project, All Rights Reserved
# initially written by J Cameron Cooper, 11 June 2003
# concept with Brent Hendricks, George Runyan

""" Groups tool interface

Goes along the lines of portal_membership, but for groups."""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class portal_groups(Interface):
    """Defines an interface for working with groups in an abstract manner.
    Parallels the portal_membership interface of CMFCore"""
    id = Attribute('id','Must be set to "portal_groups')

    def getGroupById(self, id):
        """Returns the portal_groupdata-ish object for a group corresponding
        to this id."""

    def listGroups(self):
        """Returns a list of the available portal_groupdata-ish objects."""

    def listGroupIds(self):
        """Returns a list of the available groups' ids."""

    def searchForGroups(self, REQUEST, **kw):    # maybe searchGroups()?
        """Return a list of groups meeting certain conditions. """
        # arguments need to be better refined?

    def addGroup(self, id, password, roles, domains):
        """Create a group with the supplied id, roles, and domains.

	Underlying user folder must support adding users via the usual Zope API.
	Passwords for groups seem to be currently irrelevant in GRUF."""

    def editGroup(self, id, password, roles, permissions):
        """Edit the given group with the supplied password, roles, and domains.

	Underlying user folder must support editing users via the usual Zope API.
	Passwords for groups seem to be currently irrelevant in GRUF."""

    def removeGroups(self, ids):
        """Remove the group in the provided list (if possible).

	Underlying user folder must support removing users via the usual Zope API."""

    def setGroupOwnership(self, group, object):
    	"""Make the object 'object' owned by group 'group' (a portal_groupdata-ish object)"""

    def setGroupWorkspacesFolder(self, id=""):
    	""" Set the location of the Group Workspaces folder by id.

    	The Group Workspaces Folder contains all the group workspaces, just like the
    	Members folder contains all the member folders.

     	If anyone really cares, we can probably make the id work as a path as well,
     	but for the moment it's only an id for a folder in the portal root, just like the
     	corresponding MembershipTool functionality. """

    def getGroupWorkspacesFolderId(self):
	""" Get the Group Workspaces folder object's id.

    	The Group Workspaces Folder contains all the group workspaces, just like the
    	Members folder contains all the member folders. """

    def getGroupWorkspacesFolder(self):
	""" Get the Group Workspaces folder object.

    	The Group Workspaces Folder contains all the group workspaces, just like the
    	Members folder contains all the member folders. """

    def toggleGroupWorkspacesCreation(self):
    	""" Toggles the flag for creation of a GroupWorkspaces folder upon first
        use of the group. """

    def getGroupWorkspacesCreationFlag(self):
    	"""Return the (boolean) flag indicating whether the Groups Tool will create a group workspace
        upon the next use of the group (if one doesn't exist). """

    def getGroupWorkspaceType(self):
	"""Return the Type (as in TypesTool) to make the GroupWorkspace."""

    def setGroupWorkspaceType(self, type):
	"""Set the Type (as in TypesTool) to make the GroupWorkspace. Expects the name of a Type."""

    def createGrouparea(self, id):
        """Create a space in the portal for the given group, much like member home
        folders."""

    def getGroupareaFolder(self, id):
        """Returns the object of the group's work area."""

    def getGroupareaURL(self, id):
        """Returns the full URL to the group's work area."""

    # and various roles things...

