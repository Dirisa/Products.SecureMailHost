from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *

schema = BaseSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                 description = 'More details on the question, if not evident from the title.', 
                 description_msgid = "help_detailed_question",
                 label = "Detailed Question",
                 label_msgid = "label_detailed_question",
                 rows = 5,
                 i18n_domain = "plonehelpcenter")
    ),

    TextField('answer',
              required=1,
              searchable=1,
              widget=TextAreaWidget(
    description_msgid = "desc_answer",
    label_msgid = "label_answer",
    i18n_domain = "plonehelpcenter",
    rows=10),
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
               
    LinesField('sections',
               multiValued=1,
               required=1,
               vocabulary='_get_sections_vocab', # we acquire this from
                                                 # FAQFolder
               enforceVocabulary=1,
               widget=MultiSelectionWidget(
    label='Sections',
    description='Section(s) of the FAQ that this question should appear in.',),
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
    allow_discussion = 1

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
