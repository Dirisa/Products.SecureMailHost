##############################################################################
#
#    Copyright (C) 2004 Material Thought, Inc (dba iTec Solutions)
#    and Contributors <russf@topia.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307,
#
##############################################################################
"""

$Id: tool.py,v 1.1 2004/03/24 11:30:00 dpunktnpunkt Exp $
"""

from Interface import Interface, Attribute

class IPloneClipboardTool(Interface):

    def getClipboards(create=0):
        """Returns a list of the current member's Clipboards (instances of
        ReferenceBag).

        Returns None if user is Anonymous.

        Returns the empty list if there are no Clipboards available.

        Optionally creates default clipboards if no clipboards have been
        created before (create=1).
        """

    def getClipboard(id):
        """Return the clipboard with the given id.

        Returns None if clipboard didn't exist."""

    def createClipboard(id, title=None):
        """Create a clipboard given an id and an optional title.

        Returns created ReferenceFolder instance."""


    def createDefaultClipboards():
        """Prepopulate user's clipboards directory with a set of default,
        empty clipboards."""
