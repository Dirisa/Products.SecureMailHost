#
# Tests for PHC and the Comment (discussion or talkback) system
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneHelpCenter.tests import PHCTestCase


class TestTutorialPageComments(PHCTestCase.PHCTestCase):
    """Tests related to a bug where comments on objects in a PHC Tutorial's
    items were shoting up on the tutorial itself."""

    def afterSetUp(self):
        self._createHelpCenter(self.folder, 'hc')
        self.tf = self.folder.hc.tutorial # tutorial folder
        self.tf.invokeFactory('HelpCenterTutorial', id='t')
        self.tutorial = self.tf.t
        self.tutorial.invokeFactory('HelpCenterTutorialPage', 'page1')
        self.tutorial.invokeFactory('HelpCenterTutorialPage', 'page2')
        self.tutorial.invokeFactory('HelpCenterTutorialPage', 'page3')
        
    def testCommentOnTutorialPage(self):
        title = 'Test comment'
        body = 'head\nbody\nlegs\n'
        discussionTool = self.portal.portal_discussion
        # set up the talkback subobject
        discussionTool.getDiscussionFor(self.tutorial.page2)
        # create a comment on the tutorial page
        self.tutorial.page2.discussion_reply(subject=title, body_text=body,)
        # verify that we can get it back on the page
        talkback = discussionTool.getDiscussionFor(self.tutorial.page2)
        comment = talkback.objectValues()[0]
        self.assertEqual(comment.Title(), title)
        self.assertEqual(comment.EditableBody(), body)
        # verify that the comment doesn't show up on the parent tutorial object 
        talkback = discussionTool.getDiscussionFor(self.tutorial)
        self.assertEqual(talkback.objectValues(), [])
        # verify that the comment doesn't show up on the other tutorial pages
        talkback = discussionTool.getDiscussionFor(self.tutorial.page1)
        self.assertEqual(talkback.objectValues(), [])
        talkback = discussionTool.getDiscussionFor(self.tutorial.page3)
        self.assertEqual(talkback.objectValues(), [])
        
    def testCommentOnTutorialFolder(self):
        title = 'Test folder comment'
        body = 'head\nbody\nlegs\n'
        discussionTool = self.portal.portal_discussion
        # set up the talkback subobject
        discussionTool.getDiscussionFor(self.tutorial)
        # create a comment on the tutorial
        self.tutorial.discussion_reply(subject=title, body_text=body,)
        # verify that we can get it back on the tutorial
        talkback = discussionTool.getDiscussionFor(self.tutorial)
        comment = talkback.objectValues()[0]
        self.assertEqual(comment.Title(), title)
        self.assertEqual(comment.EditableBody(), body)
        # verify that the comment doesn't show up on any of the tutorial pages
        talkback = discussionTool.getDiscussionFor(self.tutorial.page1)
        self.assertEqual(talkback.objectValues(), [])
        talkback = discussionTool.getDiscussionFor(self.tutorial.page2)
        self.assertEqual(talkback.objectValues(), [])
        talkback = discussionTool.getDiscussionFor(self.tutorial.page3)
        self.assertEqual(talkback.objectValues(), [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTutorialPageComments))
    return suite

if __name__ == '__main__':
    framework()
