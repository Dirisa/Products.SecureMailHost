from Products.Archetypes.public import BaseFolderSchema,BaseSchema, Schema
from Products.Archetypes.public import StringField, TextField,LinesField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget
from Products.Archetypes.public import RichWidget,MultiSelectionWidget
from Products.Archetypes.public import OrderedBaseFolder,BaseContent 
from Products.Archetypes.public import BaseFolder,registerType
from Products.Archetypes.public import DisplayList
from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

schema = BaseFolderSchema +  Schema((
    LinesField('sections',
                multivalued=1,
                required=1,
                vocabulary='listDocSections',
                enforceVocabulary=1,
                index='KeywordIndex',
                widget=MultiSelectionWidget(description_msgid='desc_howto_sections',
                       description='The sections to which this Howto belongs',
                       label_msgid='label_howto_sections',
                       label='Sections',
                       i18n_domain = "howto",
                       ),
                ),
    LinesField('versions',
                multivalued=1,
                vocabulary='listDocVersions',
                enforceVocabulary=1,
                accessor='Versions',
                widget=MultiSelectionWidget(format='checkbox',
                       description_msgid='desc_howto_versions',
                       description='The versions this Howto applies to',
                       label_msgid='label_howto_versions',
                       label='Versions',
                       i18n_domain = "howto",
                       ),
               ),
    TextField('body',
              searchable=1,
              required=1,
              primary=1,
              default_content_type = 'text/structured',
              default_output_type = 'text/html',
              allowable_content_types=('text/plain',
                                       'text/structured',
                                       'text/restructured',
                                       'text/html'),
              widget=RichWidget(description_msgid='desc_howto_body',
                         description='The text of the Howto',
                         label_msgid='body',
                         label='Body',
                         i18n_domain = "faq",
                         rows=25,
                         ),
              ),
    ),
    marshall=PrimaryFieldMarshaller(),
 )

class HelpCenterHowTo(BaseFolder):
    """This is a howto document content object, to which you can attach images and
    files.
    """

    content_icon = 'topic_icon.gif'

    schema = schema
    archetype_name = 'How-to'
    meta_type = 'HelpCenterHowTo'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('Image', 'File','PloneImage','PloneFile')

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/howto_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {
        'id': 'attachments',
        'name': 'Attachments',
        'action': 'string:${object_url}/howto_attachments',
        'permissions': (CMFCorePermissions.View,)
        },
        
        )

    security = ClassSecurityInfo()
    
    #method to get the defined versions to which the howto may apply
    def listDocVersions(self):
         versions = getattr(self, 'doc_versions', [])
         results = []
         for version in versions:
            results.append([version,version])
         versionstuple = tuple(results)
         return DisplayList(versionstuple)
    
    #method to get the defined sections to which the howto may belong
    def listDocSections(self):
         sections = getattr(self, 'doc_sections', [])
         results = []
         for section in sections:
            results.append([section,section])
         sectiontuple = tuple(results)
         return DisplayList(sectiontuple)
    
    security.declareProtected(CMFCorePermissions.View,'Versions')
    #method to display the versions in a nicer way
    def Versions(self):
         result=""
         for version in self.versions:
             if result:
                 result=result+", "+ version
             else:
                 result=version
         return result

registerType(HelpCenterHowTo)
