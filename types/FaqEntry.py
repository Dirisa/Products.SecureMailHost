from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseSchema + Schema((
    TextField('question',
              searchable = 1,
default_output_type = 'text/html',
              allowable_content_types = ("text/html", "text/structured"),
              widget=TextAreaWidget(label_msgid = "label_question",
                                    description_msgid = "desc_question",
                                    i18n_domain = "faq",
                                    description='Full question. If blank, defaults to title of this FAQ.',
                                    rows=4),
                                    
              ),
              
    TextField('answer',
              required = 1,
              searchable = 1,
default_output_type = 'text/html',
              allowable_content_types = ("text/html", "text/structured"),
              widget=TextAreaWidget(description_msgid = "desc_answer",
                                    label_msgid = "label_answer",
                                    i18n_domain = "faq",
                                    rows=6),
            ),
            
    LinesField('versions',
               accessor='Versions',
               index='KeywordIndex',
               vocabulary='_get_versions_vocab',
               widget=MultiSelectionWidget(label='Versions',
                                           description='Versions of Plone that apply to this FAQ question (leave blank if not version-specific)',),
               ),
               
    LinesField('sections',
               required=1,
               index='KeywordIndex',
               accessor='Sections',
               vocabulary='_get_sections_vocab',
               widget=MultiSelectionWidget(label='Sections',
                                           description='Section(s) of FAQ that this question should appear in.',),
               ),
    ))


class HelpCenterFaqEntry(BaseContent):
    """A simple archetype"""
    schema = schema
    archetype_name = 'Faq Entry'
    meta_type = 'HelpCenterFaqEntry'

    def _get_versions_vocab(self):
        return self.aq_parent._get_versions_vocab()
    
    def _get_sections_vocab(self):
        return self.aq_parent._get_sections_vocab()

    def getQuestion(self):
        return self.question or self.Title()
    
registerType(HelpCenterFaqEntry)
