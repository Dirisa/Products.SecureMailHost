import sha

from AccessControl import ClassSecurityInfo, ModuleSecurityInfo, Owned
from Acquisition import aq_inner, aq_parent, aq_base, aq_chain, aq_get
from Products import CMFCore
from Products.CMFCore.utils import getToolByName, _limitGrantedRoles, \
     _verifyActionPermissions
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore import CMFCorePermissions

from Products.Archetypes import registerType
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.Archetypes.Field import *
from Products.Archetypes.Widget import *
from Products.Archetypes.Schema import Schemata, getSchemata
from Products.Archetypes.ClassGen import ClassGenerator, Generator

from Globals import InitializeClass


from Products.Archetypes.debug import log
from DateTime import DateTime

from Products.Archetypes.ClassGen import _modes

class VarClassGen (ClassGenerator):
    
    def __init__(self, schema):
        self.schema=schema

    def generateClass(self, klass):
        #We are going to assert a few things about the class here
        #before we start, set meta_type, portal_type based on class
        #name
        klass.meta_type = klass.__name__
        klass.portal_type = klass.__name__
        klass.archetype_name = getattr(klass, 'archetype_name',
                                       self.generateName(klass))

        self.checkSchema(klass)

        fields = self.schema.fields()
        generator = Generator()
        for field in fields:
            assert not 'm' in field.mode, 'm is an implicit mode'

            #Make sure we want to muck with the class for this field
            if "c" not in field.generateMode: continue
            type = getattr(klass, 'type')
            for mode in field.mode: #(r, w)
                self.handle_mode(klass, generator, type, field, mode)
                if mode == 'w':
                    self.handle_mode(klass, generator, type, field, 'm')

        InitializeClass(klass)
    
schemadict={}

class VariableSchemaSupport:
    '''
    Mixin class to support instance-based schemas
    Attention: must be before BaseFolder or BaseContent in 
    the inheritance list, e.g:
        
    class Blorf(VariableSchemaSupport,BaseContent):
        def getSchema():
            return some schema definition...
        
    '''

    security = ClassSecurityInfo()
  
    security.declareProtected(CMFCorePermissions.View,
                              'Schemata')
    def Schemata(self):
        return getSchemata(self)

    security.declareProtected(CMFCorePermissions.View,
                              'Schema')
    def Schema(self):
        return self.getAndPrepareSchema()

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'getAndPrepareSchema')
    def getAndPrepareSchema(self):
        s = self.getSchema()
        
        # create a hash value out of the schema
        hash = sha.new(str([f.__dict__ for f in s.values()]) + \
               str(self.__class__)).hexdigest()

        if schemadict.has_key(hash): #ok we had that schema already, so take it
            schema = schemadict[hash]
        else: #make a new one and store it using the hash key
            schemadict[hash] = s
            schema = schemadict[hash]
            g = VarClassGen(schema)
            g.generateClass(self.__class__) #generate the methods
        
        return schema
    
    # supposed to be overloaded. here the object can return its own schema
    security.declareProtected(CMFCorePermissions.View,
                              'getSchema')
    def getSchema(self):
        return self.schema
      
    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'setSchema')
    def setSchema(self, schema):
        self.schema = schema
