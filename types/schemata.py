from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.PloneHelpCenter.config import *
try:
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
    PHCReferenceWidget = ReferenceBrowserWidget
except ImportError:
    PHCReferenceWidget = ReferenceWidget


#############################################################################################
# Common components to Help Types schemas

# how important the item is
ImportanceSchema = Schema((
    StringField('importance',
               required=1,
               default=IMPORTANCE_DEFAULT,
               index='KeywordIndex:schema',
               vocabulary='getImportanceVocab',
               widget=SelectionWidget(
                       label='Importance',
                       description='Importance of this item',
			description_msgid = "phc_importance",
			label_msgid = "phc_label_importance",               
			i18n_domain = "plonehelpcenter"
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
                   description_msgid = "phc_related",
                   label_msgid = "phc_label_related",               
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
                       label_msgid='phc_label_versions',
                       label= "Versions",
                       description='Versions of product that apply to this item '
                                   '(leave blank if not version-specific)',
		       description_msgid = "phc_versions",
		       i18n_domain = "plonehelpcenter"                      
		      ),
               ),
    ))
# what versions should there be? (for enclosing folders, not indiv items!)
VersionsVocabSchema = Schema((
    LinesField('versions_vocab',
               default=['0.1'],
               widget=LinesWidget(
                   label="Versions",
                   description="Define the available versions for these items.",
		   description_msgid = "phc_versions_vocab",
		   label_msgid = "phc_label_versions-vocab",               
                   i18n_domain="plonehelpcenter",
                   rows=6)
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
                        description='Section(s) that this item should appear in.',
			description_msgid = "phc_sections",
			label_msgid = "phc_label_sections",               
			i18n_domain = "plonehelpcenter"),
               ),
    ))

# what sections should there be? (for enclosing folders, not indiv items!)
SectionsVocabSchema = Schema((
    LinesField('sections_vocab',
               default=['General'],
               widget=LinesWidget(
                   label="Sections",
                   description="Define the available sections for classifying these items.",
		   description_msgid = "phc_sections_vocab",
		   label_msgid = "phc_label_sections-vocab",               
                   i18n_domain="plonehelpcenter",
                   rows=6)
               ),
    ))

# which concrente items are related to the current one
# what sections should there be? (for enclosing folders, not indiv items!)
if ENABLE_REFERENCES:    
    ReferenceSchema = Schema((
        ReferenceField('referenced_items',
                   relationship = 'PloneHelpCenter',
                   allowed_types= REFERENCEABLE_TYPES,
                   required = 0,
                   multiValued=1,                   
                   widget=PHCReferenceWidget (
                       label="Referenced Items",
                       description="Set one or more references to HelpCenter items.",
		       description_msgid = "phc_reference",
        	       label_msgid = "phc_label_reference",               
                       i18n_domain="plonehelpcenter")
                   ),
        ))
else:
    ReferenceSchema = Schema()


# non folderish Help Center Base schemata
HCSchema = BaseSchema

# folderish Help Center Base schemata
HCFolderSchema = BaseFolderSchema


#################################################################
# The type definitions
#################################################################

#####
# FAQ 
#####

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
	          description = 'Meaningful sentences that explains the answer.',
                  description_msgid = "desc_answer",
                  label_msgid = "label_answer",
                  i18n_domain = "plonehelpcenter",
                  rows=10),
              **DEFAULT_CONTENT_TYPES
              ),
    )) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema + ReferenceSchema

############
# FAQ Folder
############

FAQFolderSchema = HCFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(
			description="Description of the FAQ Container.",
			description_msgid="phc_desc_folder",
			label_msgid="phc_label_folder",
			label="Description",
			i18n_domain = "plonehelpcenter",
			rows=6)
              ),

    )) + SectionsVocabSchema

#########################
# Help Center base folder
#########################



HCRootSchema = BaseFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="phc_desc_helpcenter",
                                    description="Description for the Help Center.",
                                    label_msgid="phc_label_desc_helpcenter",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6),
              ),

    LinesField('versions_vocab',
        required=1,
        widget=LinesWidget(description_msgid="phc_version_helpcenter",
            description="Versions that items in help can refer to.",
            label="Versions",
	    label_msgid="phc_label_version_helpcenter",
            i18n_domain = "plonehelpcenter",
            ),
        ),
    ))

#######
# Howto
#######

HowToSchema = HCFolderSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                 description = 'Brief explanation of the How To.',
                 description_msgid = "phc_help_detailed_howto",
                 label = "Summary",
                 label_msgid = "phc_label_detailed_howto",
                 i18n_domain = "plonehelpcenter"
	      ),
    ),
    TextField('body',
              searchable=1,
              required=1,
              primary=1,
              widget=RichWidget(description_msgid='phc_desc_howto_body',
                         description='The text of the Howto',
                         label_msgid='phc_body',
                         label='Body',
                         i18n_domain = "plonehelpcenter",
                         rows=25,
                         ),

              **DEFAULT_CONTENT_TYPES
              ),
              ),

    marshall=PrimaryFieldMarshaller(),

 ) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema + ReferenceSchema

#############
# HowToFolder
#############

HowToFolderSchema = HCFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="phc_desc_howto_folder",
                                    description="Description for the How-to Container.",
                                    label_msgid="phc_label_howto_folder",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6)),
    )) + SectionsVocabSchema

##########
# Tutorial
##########

TutorialSchema = HCSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                 description = 'A summary of the tutorial--aims and scope. Will be displayed on every page of the tutorial.',
                 description_msgid = "phc_help_tutorial_summary",
                 label = "Tutorial Description",
                 label_msgid = "phc_label_tutorial_description",
                 rows = 5,
                 i18n_domain = "plonehelpcenter")
              ),
    ))  + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema + ReferenceSchema

################
# TutorialFolder
################

TutorialFolderSchema = HCFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="phc_desc_folder_tutorial",
                                    description="Description for the tutorials section.",
                                    label_msgid="phc_label_folder_tutorial",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6)),
    )) + SectionsVocabSchema

##############
# TutorialPage
##############

TutorialPageSchema = HCSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                  description = "Enter a brief description",
                  description_msgid = "phc_desc_tutorial_page",
                  label = "Description",
                  label_msgid = "phc_label_tutorial_page",
                  rows = 5,
                  i18n_domain = "plonehelpcenter")),

              TextField('body',
                  required = 1,
                  searchable = 1,
                  primary = 1,

                  widget = RichWidget(
                      description = "The body text.",
                      description_msgid = "phc_desc_body_tutorial",
                      label = "Body text",
                      label_msgid = "phc_label_body_tutorial",
                      rows = 25,
                      i18n_domain = "plonehelpcenter"),
                  **DEFAULT_CONTENT_TYPES
                  ))
              )

################
# ErrorReference
################

ErrorReferenceSchema = HCFolderSchema + Schema((
    TextField('description',
        default='',
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget = TextAreaWidget(
                  description = "Enter a brief description",
                  description_msgid = "phc_desc_ErrorReference",
                  label = "Description",
                  label_msgid = "phc_label_ErrorReference",
                  rows = 5,
                  i18n_domain = "plonehelpcenter"),
        ),
    TextField('body',
        searchable=1,
        required=1,
        primary=1,
        widget=RichWidget(description_msgid='phc_desc_body_ErrorReference',
            description='Explanation of the error.',
            label_msgid='phc_label_body_ErrorReference',
            label='Body',
            i18n_domain = "plonehelpcenter",
            rows=25,
            ),

        **DEFAULT_CONTENT_TYPES
        ),
        ),

    marshall=PrimaryFieldMarshaller(),

    ) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema + ReferenceSchema

######################
# ErrorReferenceFolder
######################

ErrorReferenceFolderSchema = HCFolderSchema + Schema((
    TextField('description',
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget=TextAreaWidget(description_msgid="description_edit_ErrorReference",
            description="Description for the Error Reference Container.",
            label_msgid="description_label_ErrorReference",
            label="Description",
            i18n_domain = "plonehelpcenter",
            rows=6)),
        )) + SectionsVocabSchema

######
# Link
######

LinkSchema = HCFolderSchema + Schema((
    TextField('description',
        default='',
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget = TextAreaWidget(description_msgid="description_edit_Link",
            description="Description for the Link.",
            label_msgid="description_label_Link",
            label="Description",
            i18n_domain = "plonehelpcenter"),
        ),
    StringField('url',
        searchable=1,
        required=1,
        primary=1,
        widget=StringWidget(description_msgid='phc_desc_link_url',
            description='Web address',
            label_msgid='phc_label_link_url',
            label='URL',
            i18n_domain='plonehelpcenter',
            ),
        ),
    ),

    marshall=PrimaryFieldMarshaller(),

    ) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema + ReferenceSchema

############
# LinkFolder
############

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

############
# Definition
############

DefinitionSchema = HCSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                 description = 'An explanation of the term.',
                 description_msgid = "phc_desc_definition",
                 label = "Definition",
                 label_msgid = "phc_label_definition",
                 rows = 5,
                 i18n_domain = "plonehelpcenter")
    ),
    )) + VersionsSchema + SectionsSchema + ImportanceSchema + RelatedSchema + ReferenceSchema

##########
# Glossary
##########

GlossarySchema = HCFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(
    description="Description of the Glossary.",
    description_msgid="phc_desc_folder_glossary",
    label_msgid="phc_label_folder_glossary",
    label="Description",
    i18n_domain = "plonehelpcenter",
    rows=6)
              ),

    )) + SectionsVocabSchema
