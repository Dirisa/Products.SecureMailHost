from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *
from Products.CMFCore import CMFCorePermissions
from schemata import ReferenceManualSchema
from PHCContent import PHCContent
from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo

class HelpCenterReferenceManual(PHCContent,OrderedBaseFolder):
    """A reference manual containing ReferenceManualPages,
    ReferenceManualSections, Files and Images.
    """

    __implements__ = (PHCContent.__implements__,
                      OrderedBaseFolder.__implements__,)

    schema = ReferenceManualSchema
    archetype_name = 'Reference Manual'
    meta_type='HelpCenterReferenceManual'
    content_icon = 'referencemanual_icon.gif'

    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterReferenceManualPage', 
                             'HelpCenterReferenceManualSection', 
                             'Image', 'File')
    allow_discussion = IS_DISCUSSABLE

    security = ClassSecurityInfo ()

    typeDescription= 'A Reference Manual can contain Reference Manual Pages and Sections, Images and Files. Index order is decided by the folder order, use the normal up/down arrow in the folder content view to rearrange content.'
    typeDescMsgId  = 'description_edit_referencemanual'

    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/referencemanual_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id'          : 'local_roles',
            'name'        : 'Sharing',
            'action'      : 'string:${object_url}/folder_localrole_form',
            'permissions' : (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions

    security.declareProtected (CMFCorePermissions.View, 
                                'getReferenceManualDescription')
    def getReferenceManualDescription(self):
        """ Returns the description of the ReferenceManual -- 
        convenience method for ReferenceManualPage
        """
        return self.Description()

    security.declareProtected (CMFCorePermissions.View, 'getTOC')
    def getTOC(self, current = None, states=[]):
        """Get a list which is essentially a TOC for this reference manual.
        A little flat, since doing recursive page templates is not very easy.
        
        Returns a dict containing:
        
            toc             : The table of contents (see below)
            previousIndex   : The index in of the start of the current section
            currentIndex    : The index in of the current object
            nextIndex       : The index in of the end of the current section
            parentIndex     : The index of the parent of the current object
            
        'toc' is a list of dicts, containing a flat depth-first ordering of
        the tree of sections and pages in the manual.
        
            url             : URL to the item
            number          : Section numbering of the item, e.g. "1.2.3" 
            title           : Title of the item
            description     : Description of the item
            localNumber     : Last part of 'number' - positioning among siblings
            depth           : Section-depth: top-level sections = 1
            selected        : Convenience attribute - true if this is the item
                                for the currently selected node
            parentIndex     : Index into the toc of the parent node, or -1 if
                                it is a top-level item
            
        The parameter 'current' gives the current object being viewed. If
        it is not given, 'previousIndex', 'currentIndex', 'nextIndex' and
        'parentIndex' are all -1.
        
        If it is given, however, these indexes give the index into the TOC
        of the previous and next siblings, the parent section, and of the
        object 'current' itself. The first three may be -1 if they do not
        apply.
        """
        
        # XXX: Ideally, we'd use ExtendedPathIndex and a catalogue search
        # here and in _buildTOC().
        
        filter = {'portal_type' : ['HelpCenterReferenceManualSection',
                                   'HelpCenterReferenceManualPage']}
        
        sections =  self.folderlistingFolderContents (contentFilter = filter)

        info = {    'toc' : [],
                    'previousIndex' : -1,
                    'currentIndex'  : -1,
                    'nextIndex'     : -1,
                    'parentIndex'   : -1 }
                 
        wftool = getToolByName (self, 'portal_workflow')
                           
        self._buildTOC (info, current, sections, "", 1, -1, wftool, states)
        
        # Sanity check the next item index in case we were at the end
        if info['nextIndex'] >= len (info['toc']):
            info['nextIndex'] = -1
        
        return info

    security.declarePrivate('_buildTOC')
    def _buildTOC(self, info, current, items, parentNumber, 
                    depth, parentIdx, wftool, states):
        """Helper method for building the TOC"""

        localIdx   = 0
        
        for item in items:
            
            # Skip items in ignored states
            if states and wftool and \
                wftool.getInfoFor (item, 'review_state') not in states:
                continue
            
            localNumber = localIdx + 1    
            number      = "%s%d." % (parentNumber, localNumber,)
            selected    = 0
            
            arrayIdx    = len (info['toc'])
                        
            # If this is the item we're looking for, record the relevant
            # indexes
            if current and item.absolute_url () == current.absolute_url ():            
                selected = 1
            
            
            info['toc'].append ({ 'url'         : item.absolute_url (),
                                  'number'      : number,
                                  'title'       : item.title_or_id (),
                                  'description' : item.Description (),
                                  'number'      : number,
                                  'localNumber' : localNumber,
                                  'depth'       : depth,
                                  'selected'    : selected,
                                  'parentIndex' : parentIdx,
                                    })
            
            # If this item has children, continue with them, depth-first                        
            if item.isPrincipiaFolderish:
                filter = {'portal_type' : ['HelpCenterReferenceManualSection',
                                           'HelpCenterReferenceManualPage']}
        
                children = item.folderlistingFolderContents (contentFilter = \
                                                                    filter)
                self._buildTOC (info, current, children, number, 
                                           depth + 1, arrayIdx, wftool, states)
                                    

            # Set the next/previous/parent indexes if this is the selected
            # item. This will be sanity-checked before it is returned
            if selected:
            
                info['parentIndex']   = parentIdx
                info['previousIndex'] = arrayIdx - 1
                info['currentIndex']  = arrayIdx
                info['nextIndex']       = arrayIdx + 1
                                                    
            localIdx += 1
            
   
registerType(HelpCenterReferenceManual, PROJECTNAME)

