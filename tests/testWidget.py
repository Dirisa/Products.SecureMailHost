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

    
    def testSingleValuedField(self):
        field = ReferenceField(
            'reffield',
            widget=ReferenceClipboardWidget,
            validators = ('referenceclipboardvalidator',),
            relationship = 'otherdoc',
            allowed_types = ('DDocument',)
            )

        cb = self.tool.getClipboards()[0]
        cb.manage_pasteObjects(self.folder.manage_copyObjects('doc2'))
        form = {'reffield_clipboard': cb.getId()}
        
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.assertEqual(self.doc2.UID(), value)
        self.assertEqual(field.validate(value, self.doc1, field=field), None)

        field.set(self.doc1, self.doc1.UID())
        self.assertEqual(field.get(self.doc1), self.doc1.UID())

        form.update({'reffield_replace': 1})        
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.assertEqual(field.validate(value, self.doc1, field=field), None)
        self.assertEqual(self.doc2.UID(), value)

        field.allowed_types = ('SomePortalType',)
        # type not allowed:
        self.assertNotEqual(field.validate(value, self.doc1, field=field),
                            None)

        field.allowed_type = ('DDocument',)
        cb.manage_pasteObjects(self.folder.manage_copyObjects('doc1'))
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        # value is list but field is single valued:
        self.assertNotEqual(field.validate(value, self.doc1, field=field),
                            None)

        form.update({'reffield_clipboard': '__CLEAR__'})
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.failIf(value)

        field.required = 1
        errors = {}
        field.validate(value, self.doc1, field=field, errors=errors)
        self.failUnless(errors.has_key('reffield'))


    def testMultiValuedField(self):
        field = ReferenceField(
            'reffield',
            widget=ReferenceClipboardWidget,
            validators = ('referenceclipboardvalidator',),
            multiValued = 1,
            )

        cb = self.tool.getClipboards()[0]
        cb.manage_pasteObjects(self.folder.manage_copyObjects('doc2'))
        form = {'reffield_clipboard': cb.getId()}

        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.assertEqual(self.doc2.UID(), value[0])
        field.set(self.doc1, value)

        form.update({'reffield_replace': 1})
        cb.manage_pasteObjects(self.folder.manage_copyObjects('doc1'))
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.assertEqual(len(value), 2)

        form.update({'reffield_clipboard': '__CLEAR__',
                     'reffield_replace': None})
        value, kwargs = field.widget.process_form(self.doc1, field, form)
        self.failIf(value)

        field.required = 1
        errors = {}
        field.validate(value, self.doc1, field=field, errors=errors)
        self.failUnless(errors.has_key('reffield'))


    def testGetTitles(self):
        field = ReferenceField(
            'reffield',
            widget=ReferenceClipboardWidget
            )

        self.doc1.setTitle('SomeTitle')
        self.doc1.update() # reindex

        self.assertEqual(field.widget.getTitles(self.doc1, field), [])

        field.set(self.doc1, self.doc1.UID())
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
