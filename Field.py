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
Validator and Widget for use with ReferenceField.

$Id: Field.py,v 1.2 2004/05/21 14:49:12 dpunktnpunkt Exp $
"""

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Widget import TypesWidget

try:
    from validation import validation, interfaces
except ImportError:
    from Products.validation import validation, interfaces


class ReferenceClipboardWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': 'referenceclipboardwidget',
        })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        # We want to work together with ReferenceField so we return a list
        # of UIDs.

        from Products.PloneClipboard.config import TOOLNAME
        reftool = getToolByName(instance, 'reference_catalog')
        cbtool = getToolByName(instance, TOOLNAME)

        uids = []
        clipboard = form.get('%s_clipboard' % field.getName(), empty_marker)
        replace = form.get('%s_replace' % field.getName(), empty_marker)
        
        # add all existing refs if not replace and not clear
        if replace == empty_marker and clipboard != '__CLEAR__':
            refs = reftool.getReferences(instance, field.relationship)
            for ref in refs:
                uids.append(ref.targetUID)

        # copy from ordinary copybuffer
        if clipboard == '__CB__':
            cbtool = getToolByName(instance, TOOLNAME)
            boards = cbtool.getClipboards()
            if boards: # we need a referencebag instance
                if boards[0].isCopyBufferPasteable():
                    try:
                        objects = boards[0].cb_dataItems()
                    except KeyError:
                        pass
                    else:
                        for obj in objects:
                            uids.append(obj.UID())
            
        # paste from clipboard
        if clipboard not in ('__CLEAR__', '__CB__', empty_marker):
            cb = cbtool.getClipboard(clipboard)
            for obj in cb.objectValues():
                uid = obj.UID()
                if uid not in uids:
                    uids.append(uid)

        return uids, {}

    def getTitles(self, instance, field):
        objs = field.get(instance)
        return [o.title_or_id() for o in objs]

class ReferenceClipboardValidator:
    __implements__ = (interfaces.ivalidator,)

    name = 'referenceclipboardvalidator'

    def __call__(self, value, instance, field, *args, **kwargs):

        catalog = getToolByName(instance, 'uid_catalog')

        if not value:
            return 1

        for uid in value:
            try:
                targetBrain = catalog(UID=uid)[0]
            except IndexError:
                return 'Invalid reference to %s' % uid

            if field.allowed_types and \
                   targetBrain.portal_type not in field.allowed_types:
                return 'Attempt to set reference to object to disallowed ' \
                       'type "%s".' % targetBrain.portal_type

        return 1

validation.register(ReferenceClipboardValidator())
