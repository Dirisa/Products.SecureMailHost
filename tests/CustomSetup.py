from Products.CMFPlone.setup.SetupBase import SetupWidget
from zLOG import INFO
from Products.Archetypes.utils import OrderedDict
from Products.PloneHelpCenter.config import IMPORTANCE_VOCAB_DEFAULT, IMPORTANCE_DEFAULT
import Data

def CreateRootPHC( self, portal ):
    portal.invokeFactory( 'HelpCenter',
                          id=Data.Hc.Id,
                          title=Data.Hc.Title,
                          description=Data.Hc.Desc,
                          versions_vocab=Data.Hc.Versions,
                          importance_vocab=Data.Hc.Importances,
                          defaultImportance=Data.Hc.DefaultImportance )
    helpCenter = getattr( portal, Data.Hc.Id )
    portal.portal_workflow.doActionFor( helpCenter, Data.Transition.publish )
    portal.portal_workflow.doActionFor( helpCenter.howto, Data.Transition.publish )
    portal.portal_workflow.doActionFor( helpCenter.tutorial, Data.Transition.publish )
    helpCenter.howto.sections_vocab = Data.HowtoFolder.Sections
    helpCenter.tutorial.sections_vocab = Data.TutorialFolder.Sections
    helpCenter.faq.sections_vocab = Data.FAQFolder.Sections
    return "Created a PHC instance in the root of your Plone site."

def CreateUsers( self, portal ):
    i = 0
    for user in Data.User.list:
        portal.portal_membership.addMember( user.Id, user.Password, user.Roles, [] )
        i += 1
    return "Created %d test users" % i

def CreateTutorials( self, portal ):
    i = 0
    helpCenter = getattr( portal, Data.Hc.Id )
    for content in Data.Tutorial.list:
        helpCenter.tutorial.invokeFactory( 'HelpCenterTutorial',
                                           id=content.Id,
                                           title=content.Title,
                                           description=content.Summary,
                                           versions=content.Versions,
                                           sections=content.Sections,
                                           importance=content.Importance )
        newTutorial = getattr( helpCenter.tutorial, content.Id )
        portal.plone_utils.changeOwnershipOf( newTutorial, content.Owner.Id, 1 )
        # Attach pages to the tutorial.
        for page in content.Pages:
            newTutorial.invokeFactory( 'HelpCenterTutorialPage',
                                       id=page.Id,
                                       title=page.Title,
                                       description=page.Summary,
                                       body=page.Body, )
            newPage = getattr( newTutorial, page.Id )
            portal.plone_utils.editMetadata( newPage, format=page.Format )
            # Each page should be owned by the same owner as the tutorial owner
            portal.plone_utils.changeOwnershipOf( newPage, content.Owner.Id, 1 )
        # Update the tutorial's workflow state
        if content.Transition:
            portal.portal_workflow.doActionFor( newTutorial, content.Transition )
        i += 1
    return "Created %d PHC Tutorials." % i

def CreateHowtos( self, portal ):
    i = 0
    helpCenter = getattr( portal, Data.Hc.Id )
    for content in Data.Howto.list:
        helpCenter.howto.invokeFactory( 'HelpCenterHowTo',
                                        id=content.Id,
                                        title=content.Title,
                                        description=content.Summary,
                                        body=content.Body,
                                        # try setting mimetype instead of format
                                        versions=content.Versions,
                                        sections=content.Sections,
                                        importance=content.Importance )
        newHowto = getattr( helpCenter.howto, content.Id )
        portal.plone_utils.editMetadata( newHowto, format=content.Format )
        portal.plone_utils.changeOwnershipOf( newHowto, content.Owner.Id, 1 )
        if content.Transition:
            portal.portal_workflow.doActionFor( newHowto, content.Transition )
        i += 1
    return "Created %d PHC Howtos." % i

def CreateFaqs( self, portal ):
    i = 0
    helpCenter = getattr( portal, Data.Hc.Id )
    for content in Data.FAQ.list:
        helpCenter.faq.invokeFactory( 'HelpCenterFAQ',
                                      id=content.Id,
                                      title=content.Title,
                                      description=content.Question,
                                      answer=content.Answer,
                                      versions=content.Versions,
                                      sections=content.Sections,
                                      importance=content.Importance )
        newFaq = getattr( helpCenter.faq, content.Id )
        portal.plone_utils.editMetadata( newFaq, format=content.Format )
        portal.plone_utils.changeOwnershipOf( newFaq, content.Owner.Id, 1 )
        if content.Transition:
            portal.portal_workflow.doActionFor( newFaq, content.Transition )
        i += 1
    return "Created %d PHC FAQs." % i


def CreateErrorRefs( self, portal ):
    i = 0
    return "Created %d PHC Error References." % i

def CreateDefinitions( self, portal ):
    i = 0
    return "Created %d PHC Definitions." % i

def CreateLinks( self, portal ):
    i = 0
    return "Created %d PHC Links." % i

def CreateReferenceManuals( self, portal ):
    i = 0
    return "Created %d PHC ReferenceManuals." % i

def CreateVideos( self, portal ):
    i = 0
    return "Created %d PHC Videos." % i

def CreateTestData( self, portal ):
    out = []
    out.append( CreateRootPHC( self, portal ) )
    out.append( CreateUsers( self, portal ) ) 
    out.append( CreateHowtos( self, portal ) )
    out.append( CreateTutorials( self, portal ) )
    out.append( CreateFaqs( self, portal ) )
    out.append( CreateErrorRefs( self, portal ) )
    out.append( CreateDefinitions( self, portal ) )
    out.append( CreateLinks( self, portal ) )
    out.append( CreateReferenceManuals( self, portal ) )
    out.append( CreateVideos( self, portal ) )
    return '  \n'.join( out )

functions = OrderedDict()
functions['Create Test Data'] = CreateTestData
functions['Create Test Users'] = CreateUsers
functions['Create Test PloneHelpCenter'] = CreateRootPHC
functions['Create Test Tutorials'] = CreateTutorials
functions['Create Test Howtos'] = CreateHowtos
functions['Create Test FAQs'] = CreateFaqs
functions['Create Test Error References'] = CreateReferenceManuals
functions['Create Test Definitions'] = CreateDefinitions
functions['Create Test Links'] = CreateLinks
functions['Create Test Reference Manuals'] = CreateReferenceManuals
functions['Create Test Videos'] = CreateVideos

class CustomSetup(SetupWidget):
    type = 'PloneHelpCenter Test Data'
    description = ("Scripts to generate test data for PloneHelpCenter testing.  "
                  "Generally, you'll just want to run Create Test Data since it "
                  "runs the other scripts in the correct order.  The goal here  "
                  "is to give you enough content to play with the product TTW "
                  "and to verify bugs at a functional testing level.  The Create "
                  "Test Users creates 4 test users (two members, a reviewer, and "
                  "a manager.  The Create Test PloneHelpCenter creates a "
                  "HelpCenter directly in the Plone Site root.  The HelpCenter "
                  "will have an id of hc.  This script also performs some setup, "
                  "like moving some of the contained PHC folderish items to "
                  "published.  The other scripts create some sample HelpCenter "
                  "content types with various properties (different workflow, "
                  "different owners, different sections, etc.).  Good luck, and "
                  "happy testing!")
    def setup(self):
        pass
    def delItems(self, fns):
        out = []
        out.append(('Currently there is no way to remove a function', INFO))
        return out
    def available(self): return functions.keys()
    def installed(self): return []
    def addItems(self, fns):
        out = []
        for fn in fns:
            out.append( (functions[fn]( self, self.portal ), INFO) )
            out.append( ('Function %s applied' % fn, INFO) )
        return out
