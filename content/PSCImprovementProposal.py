"""
$Id: PSCImprovementProposal.py,v 1.3 2005/03/09 18:04:43 dtremea Exp $
"""

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import registerType
from Products.Archetypes.public import OrderedBaseFolder

from Products.PloneSoftwareCenter.config import PROJECTNAME
from Products.PloneSoftwareCenter.utils import folder_modify_fti
from Products.PloneSoftwareCenter.content.schemata import PSCImprovementProposalSchema

def modify_fti(fti):
    folder_modify_fti(fti, allowed=('Image','File'))


class PSCImprovementProposal(OrderedBaseFolder):
    """What used to be a PLIP."""

    __implements__ = (OrderedBaseFolder.__implements__,)

    archetype_name = 'Improvement Proposal'
    immediate_view = default_view = 'psc_improvements_view'
    content_icon = 'improvementproposal_icon.gif'
    schema = PSCImprovementProposalSchema

    security = ClassSecurityInfo()

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/psc_improvements_view',
            'permissions': (CMFCorePermissions.View,),
        },
    )

    typeDescMsgId = 'description_edit_improvementproposal'
    typeDescription = ('An Improvement Proposal contains plans for '
                       'feature additions or improvements. Improvement '
                       'proposals may be associated with a planned or '
                       'implemented release, to generate a roadmap.')

    security.declareProtected(CMFCorePermissions.View, 'getProposalTypesVocab')
    def getProposalTypesVocab(self):
        """Get the allowed proposal types."""
        list = DisplayList()
        # Acquire the types
        types = self.aq_inner.aq_parent.getProposalTypes()
        for type in types:
            list.add(type, type)
        return list

    security.declareProtected(CMFCorePermissions.View, 'Title')
    def Title(self):
        """Return the title as "#${id}: ${title}".

        The id is the proposal number, and we want it to be associated
        with the title when it's displayed.
        """
        return '#%s: %s' % (self.getId(), self.getField('title').get(self))


registerType(PSCImprovementProposal, PROJECTNAME)
