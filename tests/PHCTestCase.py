from Testing import ZopeTestCase

# Make the boring stuff load quietly
ZopeTestCase.installProduct('CMFCore', quiet=1)
ZopeTestCase.installProduct('CMFDefault', quiet=1)
ZopeTestCase.installProduct('CMFCalendar', quiet=1)
ZopeTestCase.installProduct('CMFTopic', quiet=1)
ZopeTestCase.installProduct('DCWorkflow', quiet=1)
ZopeTestCase.installProduct('CMFActionIcons', quiet=1)
ZopeTestCase.installProduct('CMFQuickInstallerTool', quiet=1)
ZopeTestCase.installProduct('CMFFormController', quiet=1)
ZopeTestCase.installProduct('GroupUserFolder', quiet=1)
ZopeTestCase.installProduct('ZCTextIndex', quiet=1)
ZopeTestCase.installProduct('TextIndexNG2', quiet=1)
ZopeTestCase.installProduct('SecureMailHost', quiet=1)
ZopeTestCase.installProduct('CMFPlone')

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('PloneHelpCenter')

from Products.PloneTestCase import PloneTestCase

PRODUCTS = ['Archetypes', 'PloneHelpCenter']

PloneTestCase.setupPloneSite(products=PRODUCTS)


class PHCTestCase(PloneTestCase.PloneTestCase):

    defaultTitle = 'Default Testing Title'
    defaultVersions = ( 'Version 1.0', 'Version 2.0', 'Different Version1.0', )
    defaultImportances = ('Low', 'Medium', 'High', 'Life Changing', )
    defaultDefaultImportance = 'Medium'
    defaultBodyRst = """
    Bogus reST body
    ===============
    
    Here's fake body content for unit tests.
    
    * Looks like a list.
    * Smells like a list.
    * It's a list!
    
    Final content afer the list.
    """

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

    def _createHelpCenter(self, folder, id='hc', title=defaultTitle, versions=defaultVersions):
        """Creates and returns a refence to a PHC HelpCenter.
        This method publishes a HelpCenter instance under folder.  It fills in
        all of the standard properties."""
        folder.invokeFactory('HelpCenter',
                             id=id,
                             title=title,
                             description='A HelpCenter instance for unit tests.',
                             versions_vocab=versions,
                             importance_vocab=self.defaultImportances,
                             defaultImportance=self.defaultDefaultImportance )
        helpCenter = getattr(folder, id)
        self.portal.portal_workflow.doActionFor(helpCenter, 'submit')
        return helpCenter

    def _createHowto(self, howtoFolder, id, title=defaultTitle):
        """Creates and returns a refence to a PHC Howto.
        This method creates a Howto instance under a folder.  It fills in
        all of the standard properties."""
        howtoFolder.invokeFactory('HelpCenterHowTo',
                                  id=id,
                                  title=title,
                                  description='A PHC Howto for unit tests.',
                                  body=self.defaultBodyRst, 
                                  versions=('Version 2.0',),
                                  sections=('General',),
                                  importance=self.defaultDefaultImportance)
        howto = getattr(howtoFolder, id)
        self.portal.plone_utils.editMetadata(howto, format='text/x-rst')
        return howto

    def _createTutorial(self, tutorialFolder, id, title=defaultTitle, numPages=2):
        """Creates and returns a reference to a PHC Tutorial.
        This method creates a Tutorial instance under a folder.  It fills in
        all of the standard properties."""
        tutorialFolder.invokeFactory('HelpCenterTutorial',
                                     id=id,
                                     title=title,
                                     description='A PHC Tutorial for unit tests.',
                                     versions=('Version 2.0',),
                                     sections=('General',),
                                     importance=self.defaultDefaultImportance)
        tutorial = getattr(tutorialFolder, id)
        # attach pages
        for i in range(numPages):
            pageNum = i + 1
            tutorial.invokeFactory('HelpCenterTutorialPage',
                                   id='page%d' % pageNum,
                                   title='Test Tutorial Page %d' % pageNum,
                                   description='A PHC Tutorial Page (%d) for unit tests.' % pageNum,
                                   body=self.defaultBodyRst)
            newPage = getattr(tutorial, 'page%d' % pageNum)
            self.portal.plone_utils.editMetadata(newPage,format='text/x-rst')
        return tutorial
                                   
    def _createFAQ(self, faqFolder, id, title=defaultTitle):
        """Creates and returns a reference to a PHC FAQ.
        This method creates an FAQ instance under a folder.  It fills in
        all of the standard properties."""
        faqFolder.invokeFactory('HelpCenterFAQ',
                                id=id,
                                title=title,
                                description='An FAQ for unit tests.  Did you know that this field is supposed to be the question?',
                                answer='No one knows; it is one of the great mysteries.',
                                versions=('Version 2.0',),
                                sections=('General',),
                                importance=self.defaultDefaultImportance)
        faq = getattr(faqFolder, id)
        self.portal.plone_utils.editMetadata(faq, format='text/plain')
        return faq

    def _createLink(self, linkFolder, id, title=defaultTitle):
        linkFolder.invokeFactory('HelpCenterLink',
                                 id=id,
                                 title=title,
                                 description='A Link for unit tests.',
                                 url='http://www.plone.org/',
                                 versions=('Version 2.0',),
                                 sections=('General',),
                                 importance=self.defaultDefaultImportance)
        link = getattr(linkFolder, id)
        return link

    def _createErrorReference(self, errorRefFolder, id, title=defaultTitle):
        errorRefFolder.invokeFactory('HelpCenterErrorReference',
                                     id=id,
                                     title=title,
                                     description='An error reference for unit tests.',
                                     body=self.defaultBodyRst, 
                                     versions=('Version 2.0',),
                                     sections=('General',),
                                     importance=self.defaultDefaultImportance)
        errorRef = getattr(errorRefFolder, id)
        self.portal.plone_utils.editMetadata(errorRef, format='text/x-rst')
        return errorRef

    def _createDefinition(self, glossaryFolder, id, title=defaultTitle):
        glossaryFolder.invokeFactory('HelpCenterDefinition',
                                     id=id,
                                     title=title,
                                     description='A definition for unit tests.',
                                     versions=('Version 2.0',),
                                     sections=('General',),
                                     importance=self.defaultDefaultImportance)
        definition = getattr(glossaryFolder, id)
        return definition

    def _createReferenceManual(self, glossaryFolder, id, title=defaultTitle):
        pass

    def _createVideo(self, videoFolder, id, title=defaultTitle):
        pass
