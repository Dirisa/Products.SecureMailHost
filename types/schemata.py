from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.PloneHelpCenter.config import *

#############################################################################################
# Common components to Help Types schemas

# how important is this item?
ImportanceSchema = Schema((
    StringField('importance',
               required=1,
               default=IMPORTANCE_DEFAULT,
               index='KeywordIndex:schema',
               vocabulary='getImportanceVocab',
               widget=SelectionWidget(
                       label='Importance',
                       description='Importance of this item',
                      ),
               ),
    ))

# related keywords
RelatedSchema = Schema((
    LinesField('related_keywords',
               searchable=1,
               widget=LinesWidget(
                   label='Related keywords',
                   description='A list of keywords that should be indexed along with the content (e.g. for a how-to on VerboseSecurity, you might include Verbose Security, Insufficient Privileges, Debugging security problems)',
                   i18n_domain="plonehelpcenter",
                   rows=6)
               ),
    ))


# what versions does this item support?
VersionsSchema = Schema((
    LinesField('versions',
               # accessor='Versions',
               index='KeywordIndex',
               vocabulary='getVersionsVocab',
               accessor="Versions",
               multiValued=1,
               enforceVocabulary=1,
               widget=MultiSelectionWidget(
                       label='Versions',
                       description='Versions of product that apply to this item '
                                   '(leave blank if not version-specific)',
                      ),
               ),
    ))

# what sections should this item appear in?
SectionsSchema = Schema((
    LinesField('sections',
               multiValued=1,
               required=1,
               vocabulary='getSectionsVocab', # we acquire this from HelpCenter
               enforceVocabulary=1,
               index=':schema',
               widget=MultiSelectionWidget(
                        label='Sections',
                        description='Section(s) that this item should appear in.',),
               ),
    ))

# what sections should there be? (for enclosing folders, not indiv items!)
SectionsVocabSchema = Schema((
    LinesField('sections_vocab',
               default=['General'],
               widget=LinesWidget(
                   label="Sections",
                   description="Define the available sections for classifying these items.",
                   i18n_domain="plonehelpcenter",
                   rows=6)
               ),
    ))

# non folderish Help Center Base schemata
HCSchema = BaseSchema

# folderish Help Center Base schemata
HCFolderSchema = BaseFolderSchema


#############################################################################################
# Actual types

###
# FAQ 
###

FAQSchema = HCSchema + Schema((
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
              required=0,
              searchable=1,
              widget=TextAreaWidget(
                  description_msgid = "desc_answer",
                  label_msgid = "label_answer",
                  i18n_domain = "plonehelpcenter",
                  rows=10),
              **DEFAULT_CONTENT_TYPES
              ),
    )) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema

###
# FAQ Folder
###

FAQFolderSchema = HCFolderSchema + Schema((
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

    )) + SectionsVocabSchema

###
# Help Center base folder
###

HCRootSchema = BaseFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="desc_helpcenter",
                                    description="Description for the Help Center.",
                                    label_msgid="label_description",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6),
              ),

    LinesField('versions_vocab',
        required=1,
        widget=LinesWidget(
            description="Versions that items in help can refer to.",
            label="Versions"
            ),
        ),
    ))

###
# Howto
###

HowToSchema = HCFolderSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(),
    ),
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
              ),

    marshall=PrimaryFieldMarshaller(),

 ) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema

###
# HowToFolder
###

HowToFolderSchema = HCFolderSchema + Schema((
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
    )) + SectionsVocabSchema

###
# Tutorial
###

TutorialSchema = HCSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                 description = 'A summary of the tutorial--aims and scope. Will be displayed on every page of the tutorial.',
                 description_msgid = "help_tutorial_summary",
                 label = "Tutorial Description",
                 label_msgid = "label_tutorial_description",
                 rows = 5,
                 i18n_domain = "plonehelpcenter")
              ),
    ))  + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema

###
# TutorialFolder
###

TutorialFolderSchema = HCFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="desc_folder",
                                    description="Description for the tutorials section.",
                                    label_msgid="label_folder",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6)),
    )) + SectionsVocabSchema

###
# TutorialPage
###

TutorialPageSchema = HCSchema + Schema((
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
                  **DEFAULT_CONTENT_TYPES
                  ))
              )

###
# ErrorReference
###

ErrorReferenceSchema = HCFolderSchema + Schema((
    TextField('description',
        default='',
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget = TextAreaWidget(),
        ),
    TextField('body',
        searchable=1,
        required=1,
        primary=1,
        widget=RichWidget(description_msgid='desc_errorref_body',
            description='Explanation of the error.',
            label_msgid='body',
            label='Body',
            i18n_domain = "plonehelpcenter",
            rows=25,
            ),

        **DEFAULT_CONTENT_TYPES
        ),
        ),

    marshall=PrimaryFieldMarshaller(),

    ) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema

###
# ErrorReferenceFolder
###

ErrorReferenceFolderSchema = HCFolderSchema + Schema((
    TextField('description',
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget=TextAreaWidget(description_msgid="desc_folder",
            description="Description for the Error Reference Container.",
            label_msgid="label_folder",
            label="Description",
            i18n_domain = "plonehelpcenter",
            rows=6)),
        )) + SectionsVocabSchema

###
# Link
###

LinkSchema = HCFolderSchema + Schema((
    TextField('description',
        default='',
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget = TextAreaWidget(),
        ),
    StringField('url',
        searchable=1,
        required=1,
        primary=1,
        widget=StringWidget(description_msgid='desc_link_url',
            description='Web address',
            label_msgid='url',
            label='URL',
            i18ndomain='link',
            ),
        ),
    ),

    marshall=PrimaryFieldMarshaller(),

    ) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema

###
# LinkFolder
###

LinkFolderSchema = HCFolderSchema + Schema((
    TextField('description',
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget=TextAreaWidget(description_msgid="desc_folder",
            description="Description for the Link Container.",
            label_msgid="label_folder",
            label="Description",
            i18n_domain = "plonehelpcenter",
            rows=6)),
        )) + SectionsVocabSchema

###
# Definition
###

DefinitionSchema = HCSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                 description = 'An explanation of the term.',
                 description_msgid = "help_definition",
                 label = "Definition",
                 label_msgid = "label_definition",
                 rows = 5,
                 i18n_domain = "plonehelpcenter")
    ),
    )) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema

###
# Glossary
###

GlossarySchema = HCFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(
    description="Description of the Glossary.",
    description_msgid="desc_folder",
    label_msgid="label_folder",
    label="Description",
    i18n_domain = "plonehelpcenter",
    rows=6)
              ),

    )) + SectionsVocabSchema
