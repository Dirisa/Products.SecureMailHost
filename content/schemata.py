"""
$Id: schemata.py,v 1.3 2005/03/05 08:08:26 limi Exp $
"""

from Products.Archetypes.public import *
from Products.PloneSoftwareCenter.config import *
from Products.PloneSoftwareCenter.utils import changeWidgetLabel
from Products.CMFCore import CMFCorePermissions
from Products.validation import V_SUFFICIENT, V_REQUIRED
from Products.ArchAddOn.Fields import SimpleDataGridField
from Products.ArchAddOn.Widgets import SimpleDataGridWidget

# We'd like to use the ATReferenceBrowserWidget, but, at this time,
# it has enough UI sharp edges that it's hard to use. Since all
# the improvement proposals are in the same folder, there's no
# need to have people navigate a tree looking for them, and our
# custom vocab only shows the ones in your roadmap, so ...
# we're falling back to using the normal ref widget. When ATRBW
# has cleaned up it's UI, uncomment this stuff.

#try:
#from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
#         import ReferenceBrowserWidget
#except ImportError:
ReferenceBrowserWidget = ReferenceWidget

# We need to make sure that the right storage is set at Field
# creation to correctly trigger the layer registration process
if USE_EXTERNAL_STORAGE:
    from Products.ExternalStorage.ExternalStorage import ExternalStorage
    downloadableFileStorage = ExternalStorage(
        prefix=EXTERNAL_STORAGE_PATH,
        archive=False,
        rename=True,
    )
else:
    downloadableFileStorage = AttributeStorage()

TEXT_TYPES = (
    'text/structured',
    'text/x-rst',
    'text/html',
    'text/plain',
    )

IMAGE_SIZES = {
    'preview': (400, 400),
    'thumb': (128, 128),
    'tile': (64, 64),
    'icon': (32, 32),
    'listing': (16, 16),
    }
    
##############################
# ImprovementProposalContainer
##############################

PSCImprovementProposalFolderSchema = OrderedBaseFolder.schema.copy() + Schema((

    StringField(
        name='id',
        required=0,
        searchable=1,
        mode='r', # Leave the custom auto-generated ID
        widget=StringWidget (
            description="Short name of the container - this should be 'roadmap' to comply with the standards.",
            label="Short name",
            i18n_domain="archpackage",
            ),
        ),

    ComputedField(
        name='title',
        expression="'Roadmap'",
        searchable=1,
        accessor="Title",
        widget=StringWidget(
            modes=('view',)
            ),
        ),


    ComputedField(
        name='description',
        expression='"Improvement proposals for %s" % context.aq_parent.Title()',
        searchable=1,
        accessor="Description",
        widget=StringWidget(
            modes=('view',)
            ),
        ),

    ))


######################
# Improvement proposal
######################

PSCImprovementProposalSchema = OrderedBaseFolder.schema.copy() + Schema((
    
    # About the ID field:
    #
    #  The id of an improvement proposal is auto-generated via the override
    #  for generateUniqueId() found in ImprovementProposalContainer. This
    #  ensures that IDs are sequentially allocated integers, so that we can
    #  say string:Proposal #${here/getId} to get the proposal number.
    #  
    #  The id field is set to mode='r' so that it's hidden on the edit tab.
    #  However, it's still possible to rename it using the 'Rename' button
    # in folder_contents for intance and set it to a non-number. I don't
    # think we need to be that anal, though. :-)
    #
    #   - Martin (optilude)
    
    StringField(
        name='id',
        required=0,
        searchable=1,
        mode='r', # Leave the custom auto-generated ID
        widget=StringWidget (
            description="The number of the Improvement Proposal.",
            label="Proposal number",
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='proposer',
        required=1,
        searchable=1,
        widget=StringWidget(
            description="The person proposing this improvement.",
            label="Proposer",
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='seconder',
        required=0,
        searchable=1,
        widget=StringWidget(
            description="The person seconding this improvement.",
            label="Seconder",
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='description',
        required=1,
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget=TextAreaWidget(
            description="A short summary of the proposal.",
            label="Proposal Summary",
            rows=5,
            i18n_domain="archpackage",
            ),
        ),
        
    LinesField('proposalTypes',
               multiValued=1,
               required=1,
               vocabulary='getProposalTypesVocab',
               enforceVocabulary=1,
               index='KeywordIndex:schema',
               widget=MultiSelectionWidget(
                        label='Proposal types',
                        description='The type of proposal this is.',
                        description_msgid = "help_proposal_types",
                        label_msgid = "label_proposal_types",
                        i18n_domain = "archpackage"),
               ),

    TextField(
        name='definitions',
        required=0,
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="If you have any definitions for your proposal, please include them here.",
            label="Definitions",
            rows=5,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='motivation',
        required=1,
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="Why does this proposal exist and what problem does it solve?",
            label="Motivation",
            rows=20,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='assumptions',
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="Key assumptions made. What is being covered by and what is "
                        "intentionally left out of the scope of the proposal.",
            label="Assumptions",
            rows=20,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='proposal',
        required=1,
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="What needs to be done?",
            label="Proposal",
            rows=20,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='implementation',
        required=0,
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="How should it be done?",
            label="Implementation",
            rows=20,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='deliverables',
        required=0,
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="What code and documentation needs to be produced? "
                        "Standard items: Unit tests, localization, and documentation",
            label="Deliverables",
            rows=10,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='risks',
        required=0,
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="What are the risks of implementing this proposal? "
                        "What incompatibilities can it cause?",
            label="Risks",
            rows=10,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='timeline',
        required=0,
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="An approximate estimation of how long it will take to complete and "
                        "where you see it fit into the Plone versions.",
            label="Time Line",
            rows=10,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='participants',
        searchable=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="The people already identified for the implementation, if applicable.",
            label="Participants",
            rows=5,
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='branch',
        widget=StringWidget(
            description="The URL for the branch development is done on, if applicable.",
            label="Branch name/URL",
            i18n_domain="archpackage",
            ),
        ),

    ComputedField(
            name='relatedReleases',
            expression="[ {'id':o.getId(), 'url':o.absolute_url() } for o in context.getBackReferences('RelatedFeatures') ]",
            widget=StringWidget(
                label='Related Releases',
                modes=('view',),
                ),
            index=':schema',
            ),


    ))

############
# Dependency
############

# XXX: Not used now.

APDependencySchema = ExtensibleMetadataSchema + Schema((

    ReferenceField(
        name='package',
        required=1,
        searchable=1,
        allowed_types=('PSCProject',),
        enforceVocabulary=1,
        relationship='dependsOnPackage',
        widget=SelectionWidget(
            description="help_dependency_package",
            description_msgid="",
            label="Platform",
            label_msgid="label_dependency_package",
            i18n_domain="archpackage",
            ),
        ),

    ReferenceField(
        name='release',
        required=1,
        searchable=1,
        allowed_types=('PSCRelease',),
        enforceVocabulary=1,
        relationship='dependsOnRelease',
        widget=SelectionWidget(
            description="",
            description_msgid="help_dependency_version",
            label="Version",
            label_msgid="label_dependency_release",
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='dependency_type',
        required=1,
        searchable=1,
        vocabulary='_get_dependencies',
        widget=SelectionWidget(
            description="",
            description_msgid="help_dependency_type",
            label="Dependency Type",
            label_msgid="label_dependency_type",
            i18n_domain="archpackage",
            ),
        ),

    ))


#########
# Project
#########

PSCProjectSchema = OrderedBaseFolder.schema.copy() + Schema((

    TextField(
        name='description',
        default='',
        required=1,
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget=TextAreaWidget(
            description="A short summary of the project.",
            description_msgid="help_description",
            label="Project Summary",
            label_msgid="label_project_description",
            rows=5,
            i18n_domain="archpackage",
            ),
        ),

    TextField(
        name='text',
        required=1,
        searchable=1,
        primary=1,
        #validators=('isTidyHtml',),
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            description="The complete project description.",
            description_msgid="help_package_body_text",
            label="Full Project Description",
            label_msgid="label_package_body_text",
            rows=25,
            i18n_domain="archpackage",
            ),
        ),

    # recommended is intended for reviewers to select those products
    # that represent "best of breed"

    BooleanField(
        name='recommended',
        accessor="isRecommended",
        searchable=1,
        default=0,
        write_permission=CMFCorePermissions.ReviewPortalContent,
        widget=BooleanWidget(
            description="",
            description_msgid="help_package_recommended",
            label="Recommended Project",
            label_msgid="label_package_recommended",
            i18n_domain="archpackage",
            ),
        ),

    LinesField('categories',
               multiValued=1,
               required=1,
               vocabulary='getCategoriesVocab',
               enforceVocabulary=1,
               index='KeywordIndex:schema',
               widget=MultiSelectionWidget(
                        label='Categories',
                        description='Categories that this item should appear in.',
                        description_msgid = "help_categories",
                        label_msgid = "label_categories",
                        i18n_domain = "archpackage"),
               ),
               
    LinesField('currentVersions',
        required=0,
        multiValued=1,
        vocabulary='getVersions_vocab',
        widget=MultiSelectionWidget(
            description_msgid="description_current_versions",
            description="For documentation items and releases, users will be warned if the relevant version is not in this list.",
            label="Active/supported versions",
	    label_msgid="label_current_versions",
            i18n_domain = "archpackage",
            ),
        ),


    LinesField('proposalTypes',
               multiValued=1,
               required=1,
               default=['User interface', 'Architecture'],
               widget=LinesWidget(
                        label='Roadmap proposal types',
                        description='You will have a roadmap available in your project, and you can add categories of enhancement specifications below.',
                        description_msgid = "help_roadmap_types",
                        label_msgid = "label_roadmap_types",
                        i18n_domain = "archpackage"),
               ),


    StringField(
        name='homepage',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            description="The project's home page - if different from this.",
            description_msgid="help_package_homepage",
            label="Home page ",
            label_msgid="label_package_homepage",
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='repository',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            description="Either the repository itself, or a repository page, if it exists.",
            description_msgid="help_package_repository",
            label="URL of version control repository",
            label_msgid="label_package_repository",
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='tracker',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            description="URL of issue tracker, if the project has one.",
            description_msgid="help_package_tracker",
            label="Issue tracker URL",
            label_msgid="label_package_tracker",
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='mailingList',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            description="URL of mailing list information page/archives or support forum, if the project has one.",
            description_msgid="help_package_mailinglist",
            label="Support mailing list or forum URL",
            label_msgid="label_package_mailinglist",
            i18n_domain="archpackage",
            ),
        ),

    StringField(
        name='contact_email',
        required=1,
        validators=('isEmail',),
        widget=StringWidget(
            description="This will not be exposed publicly.",
            description_msgid="help_package_contact_email",
            label="Contact email",
            label_msgid="label_package_contact_email",
            i18n_domain="archpackage",
            ),
        ),

    ImageField(
        name='logo',
        required=0,
        original_size=(300,150),
        sizes=IMAGE_SIZES,
        widget=ImageWidget(
            description="Add a logo for the project (or company) by clicking the 'Browse' button. Max 300x150 pixels (will be resized if bigger).",
            description_msgid="help_package_logo",
            label= "Logo",
            label_msgid="label_package_logo",
            i18n_domain="archpackage",
            ),
        ),

    ImageField(
        name='screenshot',
        required=0,
        original_size=(800,600),
        sizes=IMAGE_SIZES,
        widget=ImageWidget(
            description="Add a screenshot by clicking the 'Browse' button. Max 800x600 (will be resized if bigger).",
            description_msgid="help_package_screenshot",
            label= "Screenshot",
            label_msgid="label_package_screenshot",
            i18n_domain="archpackage",
            ),
        ),

    ))

###############
# ReleaseFolder
###############

PSCReleaseFolderSchema = OrderedBaseFolder.schema.copy() + Schema((

    StringField(
        name='id',
        required=0,
        searchable=1,
        mode='r', # Leave the custom auto-generated ID
        widget=StringWidget (
            description="Short name of the container - this should be 'release' to comply with the standards.",
            label="Short name",
            i18n_domain="archpackage",
            ),
        ),

    ComputedField(
        name='title',
        expression="'Releases'",
        searchable=1,
        accessor="Title",
        widget=StringWidget(
            modes=('view',)
            ),
        ),

    ComputedField(
        name='description',
        expression='"Available releases of %s." % context.aq_parent.Title()',
        searchable=1,
        accessor="Description",
        widget=StringWidget(
            modes=('view',)
            ),
        ),

    ))


#########
# Release
#########

PSCReleaseSchema = OrderedBaseFolder.schema.copy() + Schema((

    StringField(
        name='id',
        required=1,
        searchable=1,
        mode="rw",
        accessor="getId",
        mutator="setId",
        default=None,
        widget=StringWidget(
            label='Version',
            label_msgid='label_release_version',
            description="Release version--this field is also used in the URL "
                        "of the item, so don't use spaces and special "
                        "characters.",
            description_msgid='help_release_version',
            i18n_domain='archpackage',
        ),
    ),
    
    ComputedField('title',
            accessor='Title',
            expression="context.generateTitle ()",
            mode='r',
            widget=ComputedWidget
            (description="The title of the release, computed from the title of the package and the version number.",
                i18n_domain='archpackage',
                label="Release title",
                modes=('view',),
                visible={'edit' : 'invisible',
                        'view' : 'visible' },
            ),
        ),


    StringField(
            name='codename',
            required=0,
            searchable=1,
            widget=StringWidget(
                label='Codename',
                description='Codename for this release, if you have one.',
                description_msgid='help_release_codename_description',
                label_msgid='help_release_codename_label',
                i18n_domain='archpackage',
                ),
            ),

    TextField('description',
        default='',
        searchable=1,
        required=1,
        accessor='Description',
        storage=MetadataStorage(),
        widget=TextAreaWidget(
            description='A short description of the most important '
                        'focus of this release. Not a version history, '
                        'but in plain text what the main benefit of '
                        'this release is.',
            description_msgid='help_release_description',
            label='Release Summary',
            label_msgid='label_release_description',
            rows=5,
            i18n_domain='archpackage',
        ),
    ),

    TextField(
        name='text',
        searchable=1,
        primary=1,
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            label='Full Release Description',
            label_msgid='label_release_body_text',
            description='The complete release text.',
            description_msgid='help_release_body_text',
            rows=25,
            i18n_domain='archpackage',
        ),
    ),

    TextField(
        name='changelog',
        required=0,
        searchable=1,
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=TEXT_TYPES,
        widget=RichWidget(
            label='Changelog',
            label_msgid='label_release_changelog',
            description='A detailed log of what has changed since the previous release.',
            description_msgid='help_release_changelog',
            rows=25,
            i18n_domain='archpackage',
        ),
    ),

    StringField('releaseManager',
            required=0,
            searchable=1,
            widget=StringWidget(
                label='Release Manager',
                description='Release manager for this release.',
                description_msgid='help_release_relmgr_description',
                label_msgid='help_release_relmgr_label',
                i18n_domain='archpackage',
                ),
            ),

    DateTimeField('expectedReleaseDate',
            required=0,
            searchable=0,
            widget=CalendarWidget(
                label='Expected Release Date',
                label_msgid='help_release_expected_date_label',
                i18n_domain='archpackage',
                ),
            ),

    

    StringField(
        name='license',
        required=1,
        vocabulary='getLicenseVocab',
        widget=SelectionWidget(
            label='License',
            label_msgid='label_release_license',
            description='Release License',
            description_msgid='help_release_license',
            i18n_domain='archpackage',
        ),
    ),

    LinesField(
        name='compatibility',
        required=0,
        searchable=1,
        vocabulary='getCompatibilityVocab',
        widget=MultiSelectionWidget(
            label='Compatibility',
            label_msgid='label_release_compatibility',
            description='Tested and working with the following versions:',
            description_msgid='help_release_compatibility',
            i18n_domain='archpackage',
        ),
    ),

    StringField(
        name='maturity',
        required=1,
        searchable=1,
        vocabulary='getMaturityVocab',
        widget=SelectionWidget(
            label='Maturity',
            label_msgid='label_release_maturity',
            description='Release Maturity',
            description_msgid='help_release_maturity',
            i18n_domain='archpackage',
        ),
    ),

    ImageField(
        name='screenshot',
        required=0,
        original_size=(800,600),
        sizes=IMAGE_SIZES,
        widget=ImageWidget(
            label='Screenshot',
            label_msgid='label_release_screenshot',
            description='Add a screenshot by clicking the \'Browse\' '
                          'button. Add a screenshot that highlights the '
                          'features in this specific release. If you '
                          'don\'t add a file, it will default to the '
                          'screenshot for the project. Max 800x600 pixels.',
            description_msgid='help_release_screenshot',
            i18n_domain='archpackage',
        ),
    ),
    
    ReferenceField('relatedFeatures',
            allowed_types=('PSCImprovementProposal',),
            multiValued=1,
            relationship='RelatedFeatures',
            widget=ReferenceBrowserWidget(
                startup_directory="../%s" % (IMPROVEMENTS_ID,),
                description="Please select related improvement proposals for features going into this release.",
                label='Associated feature proposals',
                i18n_domain='archpackage',
            ),
            vocabulary='getRelatedFeaturesVocab',
        ),

    StringField(
        name='repository',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            description_msgid="help_release_repository",
            label="Repository branch",
            description="URL of version control repository branch for this release.",
            label_msgid="label_release_repository",
            i18n_domain="archpackage",
            ),
        ),

    #StringField(
    #    name='populate',
    #    mutator='populateFrom',
    #    required=0,
    #    vocabulary='_get_releases',
    #    widget=SelectionWidget(
    #        label='Initialize Dependencies',
    #        description='Choose a release to use as a base for the '
    #                      'dependencies for this release. Normally '
    #                      'you use the previous release.',
    #        visible={'view': 'hidden', 'edit': 'visible'},
    #        ),
    #    ),

    ComputedField(
            name='ProjectURL',
            expression='context.aq_parent.getProjectURL()',
            index='FieldIndex:schema',
            widget=StringWidget(
                modes=('view',),
                label='Project URL',
                description='URL of project for this release.',
                ),
            ),

    ))


######
# File
######

PSCFileSchema = BaseSchema.copy()


PSCFileSchema += Schema((

    TextField(
        name='title',
        default='',
        searchable=1,
        accessor="Title",
        widget=StringWidget(
            description="File description. Normally something like "
                        "'Product Package', 'Windows Installer',  - "
                        "or 'Events subsystem' if you have several "
                        "separate modules. The actual file name will "
                        "be the same as the file you upload.",
            description_msgid="help_file_title",
            label="File Description",
            label_msgid="label_file_title",
            i18n_domain="archpackage",
        ),
    ),

    FileField(
        name='downloadableFile',
        primary=1,
        required=1,
        widget=FileWidget(
            description="Click 'Browse' to upload a release file.",
            description_msgid="help_file_description",
            label="File",
            label_msgid="label_file_description",
            i18n_domain="archpackage",
        ),
        storage=downloadableFileStorage,
    ),

    StringField(
        name='platform',
        required=1,
        searchable=0,
        vocabulary='getPlatformVocab',
        widget=SelectionWidget(
            description="",
            description_msgid="help_file_platform",
            label="Platform",
            label_msgid="label_file_platform",
            i18n_domain="archpackage",
        ),
    ),

    ),

    marshall = PrimaryFieldMarshaller(),

    )

###########
# File link
###########

PSCFileLinkSchema = BaseSchema.copy()


PSCFileLinkSchema += Schema((

    TextField(
        name='title',
        default='',
        searchable=1,
        accessor="Title",
        widget=StringWidget(
            description="File description. Normally something like "
                        "'Product Package', 'Windows Installer',  - "
                        "or 'Events subsystem' if you have several "
                        "separate modules. The actual file name will "
                        "be the same as the file you upload.",
            description_msgid="help_file_title",
            label="File Description",
            label_msgid="label_file_title",
            i18n_domain="archpackage",
        ),
    ),

    StringField(
        name='platform',
        required=1,
        searchable=0,
        vocabulary='getPlatformVocab',
        widget=SelectionWidget(
            description="",
            description_msgid="help_file_platform",
            label="Platform",
            label_msgid="label_file_platform",
            i18n_domain="archpackage",
        ),
    ),

    StringField(
        name='externalURL',
        required=1,
        validators=('isURL',),
        widget=StringWidget(
            description="Please enter the URL where the file is hosted.",
            description_msgid="help_file_ext_url",
            label="URL for externally hosted file",
            label_msgid="label_file_ext_url",
            i18n_domain="archpackage",
        ),
    ),

    ),
    )
    
##############
# Package area
##############

PloneSoftwareCenterSchema = OrderedBaseFolder.schema.copy() + Schema((

    TextField('description',
        searchable=1,
        accessor='Description',
        storage=MetadataStorage(),
        widget=TextAreaWidget(
            description_msgid='help_package_area',
            description='Description for the Software Package area.',
            label_msgid='label_package_area',
            label='Description',
            i18n_domain='archpackage',
            rows=6,
        ),
    ),

    LinesField('availableCategories',
        default=['Stand-alone products', 'Add-on components', 'Infrastructure'],
        widget=LinesWidget(
            label='Categories',
            description='Define the available categories for classifying these packages.',
            description_msgid='help_categories_vocab',
            label_msgid='label_categories_vocab',
            i18n_domain='archpackage',
            rows=6,
        ),
    ),


    SimpleDataGridField('availableLicenses',
        default=['GPL|GPL - GNU General Public License|http://opensource.org/licenses/gpl-license',
                 'LGPL|LGPL - GNU Lesser General Public License|http://opensource.org/licenses/lgpl-license',
                 'BSD|BSD License (revised)|http://opensource.org/licenses/bsd-license',
                 'Freeware|Freeware|http://wikipedia.org/Freeware',
                 'Public Domain|Public Domain|http://creativecommons.org/licenses/publicdomain',
                 'OSI|Other OSI Approved|http://opensource.org/licenses',
                 'ZPL|Zope Public License (ZPL)|http://opensource.org/licenses/zpl',
                 'Commercial|Commercial License|http://plone.org/documentation/faq/plone-license'],
        widget=SimpleDataGridWidget(
            label='Licenses',
            description='Define the available licenses for software releases. The format is Name|URL.',
            i18n_domain='archpackage',
            rows=6,
        ),
    ),
    
    LinesField('availableVersions',
        default=['Plone 1.0',
                 'Plone 1.0.1',
                 'Plone 1.0.2',
                 'Plone 1.0.3',
                 'Plone 1.0.4',
                 'Plone 1.0.5',
                 'Plone 2.0'],
        widget=LinesWidget(
            label='Versions',
            description='Define the vocabulary for versions that software releases can be listed as being compatible with.',
            i18n_domain='archpackage',
            rows=6,
        ),
    ),

    SimpleDataGridField('availableMaturities',
        default=[
            'Final|Final Release - Ready for production sites',
            'RC|Release Candidate - Final testing stages',
            'Beta|Beta - Stable API, but may still have bugs',
            'Alpha|Alpha - Unstable, early development',
            'In progress|In progress - Still under active development, not released yet',
            ],
        widget=SimpleDataGridWidget(
            label='Release maturities',
            description='Define the available maturity states for software releases. Format is Name|Description',
            i18n_domain='archpackage',
            rows=6,
        ),
    ),

    LinesField('availablePlatforms',
        default=[
            'all platforms', 
            'Linux', 
            'Mac OS X', 
            'Windows',
            'BSD', 
            'UNIX (other)'
            ],
        widget=LinesWidget(
            label='Platforms',
            description='Define the available platforms for software files.',
            i18n_domain='archpackage',
            rows=6,
        ),
    ),
    
    

    ))
