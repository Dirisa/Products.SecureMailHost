#
# The Plone Help Center container.
#
# A Help Center is pre-populated with the following folders:
#
# /faq - contains the FAQ objects
# /howto - contains the How-tos
# /tutorial - contains the tutorials
# /error - contains the error references
# /link - contains the links to other documentation
# /glossary - contains the definitions
# /video - contains video files for training/instruction
# /manual - contains reference manuals
#
# The main goals of these folders are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HCRootSchema

class HelpCenter(OrderedBaseFolder):
    """A simple folderish archetype"""
    schema = HCRootSchema

    content_icon = 'helpcenter_icon.gif'

    archetype_name = 'Help Center'
    meta_type = 'HelpCenter'
    filter_content_types = 1
    allowed_content_types = ( 'HelpCenterFAQFolder'
                            , 'HelpCenterHowToFolder'
                            , 'HelpCenterTutorialFolder'
                            , 'HelpCenterReferenceManualFolder'
                            , 'HelpCenterInstructionalVideoFolder'
                            , 'HelpCenterLinkFolder'
                            , 'HelpCenterErrorReferenceFolder'
                            , 'HelpCenterGlossary' )

    security = ClassSecurityInfo()

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/helpcenter_view',
            'permissions': (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    )

    def initializeArchetype(self, **kwargs):
        # prepopulate folder
        BaseFolder.initializeArchetype(self,**kwargs)

        if 'faq' not in self.objectIds():
            self.invokeFactory('HelpCenterFAQFolder','faq')
            self['faq'].setTitle(self.translate(
					msgid='phc_faq_title',
					domain='plonehelpcenter',
					default='FAQs'))
            self['faq'].setDescription(self.translate(
					msgid='phc_faq_description',
					domain='plonehelpcenter',
					default='Frequently Asked Questions'))

        if 'howto' not in self.objectIds():
            self.invokeFactory('HelpCenterHowToFolder','howto')
            self['howto'].setTitle(self.translate(
					msgid='phc_howto_title',
					domain='plonehelpcenter',
					default='How-tos'))
            self['howto'].setDescription(self.translate(
					msgid='phc_howto_description',
					domain='plonehelpcenter',
					default='Step-by-step instructions.'))

        if 'tutorial' not in self.objectIds():
            self.invokeFactory('HelpCenterTutorialFolder','tutorial')
            self['tutorial'].setTitle(self.translate(
					msgid='phc_tutorial_title',
					domain='plonehelpcenter',
					default='Tutorials'))
            self['tutorial'].setDescription(self.translate(
					msgid='phc_tutorial_description',
					domain='plonehelpcenter',
					default='Detailed tutorials.'))

        if 'manual' not in self.objectIds():
            self.invokeFactory('HelpCenterReferenceManualFolder','manual')
            self['manual'].setTitle(self.translate(
					msgid='phc_referencemanual_title',
					domain='plonehelpcenter',
					default='Reference Manuals'))
            self['manual'].setDescription(self.translate(
					msgid='phc_referencemanual_description',
					domain='plonehelpcenter',
					default='Reference manuals for larger projects.'))


        if 'video' not in self.objectIds():
            self.invokeFactory('HelpCenterInstructionalVideoFolder','video')
            self['video'].setTitle(self.translate(
					msgid='phc_video_title',
					domain='plonehelpcenter',
					default='Videos'))
            self['video'].setDescription(self.translate(
					msgid='phc_video_description',
					domain='plonehelpcenter',
					default='Instructional videos.'))

        if 'error' not in self.objectIds():
            self.invokeFactory('HelpCenterErrorReferenceFolder','error')
            self['error'].setTitle(self.translate(
					msgid='phc_errorreference_title',
					domain='plonehelpcenter',
					default='Error References'))
            self['error'].setDescription(self.translate(
					msgid='phc_errorreference_description',
					domain='plonehelpcenter',
					default='Error reference section.'))

        if 'link' not in self.objectIds():
            self.invokeFactory('HelpCenterLinkFolder','link')
            self['link'].setTitle(self.translate(
					msgid='phc_links_title',
					domain='plonehelpcenter',
					default='Links'))
            self['link'].setDescription(self.translate(
					msgid='phc_links_description',
					domain='plonehelpcenter',
					default='Links section.'))

        if 'glossary' not in self.objectIds():
            self.invokeFactory('HelpCenterGlossary','glossary')
            self['glossary'].setTitle(self.translate(
					msgid='phc_glossary_title',
					domain='plonehelpcenter',
					default='Glossary Definitions'))
            self['glossary'].setDescription(self.translate(
					msgid='phc_glossary_description',
					domain='plonehelpcenter',
					default='Glossary of terms.'))

registerType(HelpCenter, PROJECTNAME)
