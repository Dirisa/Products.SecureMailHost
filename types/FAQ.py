from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *

schema = BaseSchema + Schema((
    TextField('question',
              searchable=1,
              widget=TextAreaWidget(
    label_msgid="label_question",
    description_msgid = "desc_question",
    i18n_domain = "plonehelpcenter",
    description='Full question. If blank, defaults to title of this FAQ.',
    rows=4),
              **DEFAULT_CONTENT_TYPES
              ),

    TextField('answer',
              required=1,
              searchable=1,
              widget=TextAreaWidget(
    description_msgid = "desc_answer",
    label_msgid = "label_answer",
    i18n_domain = "plonehelpcenter",
    rows=6),
              **DEFAULT_CONTENT_TYPES
              ),
            
    LinesField('versions',
               accessor='Versions',
               index='KeywordIndex',
               vocabulary='_get_versions_vocab',
               widget=MultiSelectionWidget(
    label='Versions',
    description='Versions of Plone that apply to this FAQ question '
    '(leave blank if not version-specific)',),
               ),
               
    LinesField('subject',
               multiValued=1,
               required=1,
               accessor="Subject",
               vocabulary='_get_sections_vocab', # we acquire this from
                                                 # FAQFolder
               enforceVocabulary=1,
               widget=MultiSelectionWidget(
    label='Sections',
    description='Section(s) of FAQ that this question should appear in.',),
               ),
    ))


class HelpCenterFAQ(BaseContent):
    """A simple archetype"""

    typeDescription= 'You can add a Frequently Asked Question (preferrably with an answer), and it will be reviewed and approved by our documentation team.'
    typeDescMsgId  = 'description_edit_faq'

    content_icon = 'faq_icon.gif'

    schema = schema
    archetype_name = 'FAQ'
    meta_type = 'HelpCenterFAQ'
    global_allow = 0

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'string:${object_url}/faq_view',
                'permissions': (CMFCorePermissions.View,)
                },)

    security = ClassSecurityInfo()

    def _get_versions_vocab(self):
        return self.aq_parent._get_versions_vocab()
    
    def _get_sections_vocab(self):
        return self.aq_parent._get_sections_vocab()

    
registerType(HelpCenterFAQ, PROJECTNAME)
