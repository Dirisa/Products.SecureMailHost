from Products.Archetypes.public import *
from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *

schema = BaseFolderSchema +  Schema((
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

class HelpCenterHowTo(BaseFolder):
    """This is a howto document content object, to which you can attach images and
    files.
    """

    content_icon = 'howto_icon.gif'

    schema = schema
    archetype_name = 'How-to'
    meta_type = 'HelpCenterHowTo'
    global_allow = 0
    filter_content_types = 1
    allow_discussion = 1
    allowed_content_types = ('Image', 'File', 'PloneImage', 'PloneFile', )

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
        'permissions': (CMFCorePermissions.ModifyPortalContent,)
        },
        
        )

    security = ClassSecurityInfo()
    
    def _get_versions_vocab(self):
        return self.aq_parent._get_versions_vocab()
    
    def _get_sections_vocab(self):
        return self.aq_parent._get_sections_vocab()

    security.declareProtected(CMFCorePermissions.View,'Versions')
    #
    def Versions(self):
        """method to display the versions in a nicer way
        """

        # XXX is this really necessary? the widget supports this, doesn't it? ~limi
        result=""
        for version in self.versions:
            if result:
                result=result+", "+ version
            else:
                result=version
        return result


registerType(HelpCenterHowTo, PROJECTNAME)
