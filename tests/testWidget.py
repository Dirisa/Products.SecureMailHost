import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.Archetypes.public import *
from Products.PloneClipboard import ReferenceClipboardWidget
from Products.PloneClipboard.config import *
import common
common.installProducts()

class TestWidget(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        common.installWithinPortal(self.portal)

        for id in ('doc1', 'doc2'):
            self.folder.invokeFactory('DDocument', id)
            setattr(self, id, getattr(self.folder, id))

        self.tool = tool = getattr(self.portal, TOOLNAME)
        tool.createDefaultClipboards()

    
    def testProcessForm(self):
        field = ReferenceField(
            'reffield',
            widget=ReferenceClipboardWidget,
            validators = ('referenceclipboardvalidator',),
            relationship = 'otherdoc',
            allowed_types = ('DDocument',)
            )

        # Let's get the first of our clipboards and paste the 'doc2'
        # object into it.
        cb1 = self.tool.getClipboards()[0]
        cb1.manage_pasteObjects(self.folder.manage_copyObjects('doc2'))

        # We leave the second clipboard empty.
        cb2 = self.tool.getClipboards()[1]        

        # 'reffield_clipboard' is the id of the input element that
        # selects the clipboard to be used as the source in the
        # widget.
        form = {'reffield_clipboard': cb1.getId()}
        
        # We use these form values to call process_form on the widget,
        # which returns a list of UIDs.  In this case the list
        # consists of one element: the doc2 object that we pasted into
        # our clipboard:
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.assertEqual([self.doc2.UID()], value)

        # We use the returned value to call field.validate, which in
        # turn calls our validator.  'None' indicates that there was
        # no error.
        self.assertEqual(field.validate(value, self.doc1), None)

        # Now we call the field's set method.
        field.set(self.doc1, value, **kwargs)

        # At this point the reference got set and we can use
        # process_form to add the contents of the second clipboard to
        # the references we already have.
        cb2.manage_pasteObjects(self.folder.manage_copyObjects('doc1'))
        form = {'reffield_clipboard': cb2.getId()}
        value, kwargs = field.widget.process_form(self.doc1, field, form)

        # To the effect that both UIDs are in value now:
        self.failUnless(self.doc1.UID() in value)
        self.failUnless(self.doc2.UID() in value)
        self.assertEqual(len(value), 2)

        # 'reffield_replace' in the replace indicates that we want to
        # replace old values.
        form = {'reffield_replace': 1}
        # Let's replace with the contents of the second clipboard:
        form['reffield_clipboard'] = cb2.getId()
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.assertEqual([self.doc1.UID()], value)

        # '__CLEAR__' indicates that we want to unset the values.
        form.update({'reffield_clipboard': '__CLEAR__'})
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.failIf(value)

    def testValidator(self):
        # Here we test the "referenceclipboardvalidator".
        field = ReferenceField(
            'reffield',
            widget=ReferenceClipboardWidget,
            validators = ('referenceclipboardvalidator',),
            relationship = 'somerel',
            )

        # First we attempt to set an invalid UID:
        res = field.validate(['invalid UID'], self.doc1)
        self.assertNotEqual(res, None)
        
        # Now we try to set multiple references with a single valued reffield.
        # (A reffield is single valued by default.)
        res = field.validate([self.doc1.UID(), self.doc2.UID()], self.doc1)
        self.assertNotEquals(res, None)

        # Set multiValued=1.  Now the last call to field.validate()
        # should be ok.
        field.multiValued = 1
        res = field.validate([self.doc1.UID(), self.doc2.UID()], self.doc1)
        self.assertEqual(res, None)

        # Let's attempt to set a reference to a disallowed type.  The
        # validator must fail here.
        field.allowed_types = ('SomePortalType',)
        res = field.validate([self.doc1.UID()], self.doc1)
        self.assertNotEqual(res, None)

        # While with an allowed type it should work:
        field.allowed_types = (self.doc1.portal_type,)
        res = field.validate([self.doc1.UID()], self.doc1)
        self.assertEqual(res, None)

    def testGetTitles(self):
        field = ReferenceField(
            'reffield',
            widget=ReferenceClipboardWidget
            )

        self.doc1.setTitle('SomeTitle')
        self.doc1.update() # reindex

        self.assertEqual(field.widget.getTitles(self.doc1, field), [])

        field.set(self.doc1, [self.doc1.UID()])
        self.assertEqual(field.widget.getTitles(self.doc1, field),
                         ['SomeTitle'])


if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestWidget))
        return suite
