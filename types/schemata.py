from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.PloneHelpCenter.config import *

FAQSchema = BaseSchema + Schema((
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

###
#
###

FAQFolderSchema = BaseFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(
    description="Description of the FAQ Container.",
    description_msgid="desc_folder",
    label_msgid="label_folder",
    label="Description",
    i18n_domain = "plonehelpcenter",
    rows=6)
              ),
    
    LinesField('sections',
               default=['General'],
               widget=LinesWidget(
    label="Sections",
    description="Define the available sections a FAQ can be assigned to.",
    i18n_domain="plonehelpcenter",
    rows=6)
               ),
    ))

###
#
###

HelpCenterSchema = BaseFolderSchema + Schema((

    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="desc_helpcenter",
                                    description="Description for the Help Center.",
                                    label_msgid="label_description",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6)),

    LinesField('versions',
                widget=LinesWidget(description="The available versions of the product, one version on each line.",
                                            label="Versions",
                                            i18n_domain = "plonehelpcenter",
                                            rows=6)),
    ))

###
#
###

HowToSchema = BaseFolderSchema +  Schema((
    TextField('body',
              searchable=1,
              required=1,
              primary=1,
              widget=RichWidget(description_msgid='desc_howto_body',
                         description='The text of the Howto',
                         label_msgid='body',
                         label='Body',
                         i18n_domain = "faq",
                         rows=25,
                         ),

              **DEFAULT_CONTENT_TYPES
              ),

    LinesField('versions',
                multivalued=1,
                vocabulary='_get_versions_vocab',
                enforceVocabulary=1,
                accessor='Versions',
                index='KeywordIndex',
                widget=MultiSelectionWidget(
                       description_msgid='desc_howto_versions',
                       description='The versions this Howto applies to',
                       label_msgid='label_howto_versions',
                       label='Versions',
                       i18n_domain = "howto",
                       ),
               ),
    LinesField('sections',
               multiValued=1,
               required=1,
               vocabulary='_get_sections_vocab',
               enforceVocabulary=1,
               widget=MultiSelectionWidget(
    label='Sections',
    label_msgid='label_howto_sections',
    description='Section(s) that this How-to should appear in.',),
    description_msgid='desc_howto_sections',
    i18n_domain = "plonehelpcenter",
               )),

    marshall=PrimaryFieldMarshaller(),
    
 )

###
#
###

HowToFolderSchema = BaseFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="desc_folder",
                                    description="Description for the How-to Container.",
                                    label_msgid="label_folder",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6)),
    LinesField('sections',
               default=['General'],
               widget=LinesWidget(
    label="Sections",
    description="Define the available sections a How-to can be assigned to.",
    i18n_domain="plonehelpcenter",
    rows=6)
               ),
    ))

###
#
###

TutorialSchema = BaseSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                 description = 'A summary of the tutorial -  aims and scope. Will be displayed on every page of the tutorial.', 
                 description_msgid = "help_tutorial_summary",
                 label = "Tutorial Description",
                 label_msgid = "label_tutorial_description",
                 rows = 5,
                 i18n_domain = "plonehelpcenter")
    ),

    LinesField('sections',
               multiValued=1,
               required=1,
               vocabulary='_get_sections_vocab', # we acquire this from
                                                 # FAQFolder
               enforceVocabulary=1,
               widget=MultiSelectionWidget(
    label='Sections',
    description='Section(s) of the tutorials listing that this should appear in.',),
               ),
))

###
#
###

TutorialFolderSchema = BaseFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="desc_folder",
                                    description="Description for the Tutorial Container.",
                                    label_msgid="label_folder",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6)),
    LinesField('sections',
               default=['General'],
               widget=LinesWidget(
    label="Sections",
    description="Define the available sections a How-to can be assigned to.",
    i18n_domain="plonehelpcenter",
    rows=6)
               ),
    ))

###
#
###

TutorialPageSchema = BaseSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
    description = "Enter a brief description", 
    description_msgid = "help_description",
    label = "Description",
    label_msgid = "label_description",
    rows = 5,
    i18n_domain = "plone")),
    
    TextField('body',
              required = 1,
              searchable = 1,
              primary = 1,
              
              widget = RichWidget(
    description = "The body text.",
    description_msgid = "help_body_text",
    label = "Body text",
    label_msgid = "label_body_text",
    rows = 25,
    i18n_domain = "plone"),
    **DEFAULT_CONTENT_TYPES))
                             )

