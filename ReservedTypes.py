"""
This module depends on Archetypes which depends on CMF and possibly
Plone, so install them.

ReservedTypes provides services for portal_type instances that are
meant to have static ids and titles within certain other portal_type
instances.  The instances with static ids and titles are called the
reservee and the instances containing them are called the reservers.
The common case where a class is meant to do both is called reserved.
If I can find a way, I will lose the restriction that this module must
be used in the code of both the reservee and the reserver.

A reservee class must have three string attributes: id, title, and
archetype_name.  What would be _res_type is assumed from the class name as
the same assumption is made elsewhere in Archetypes.  A reservee class
must also call either registerTypeAsReservee(klass) or
registerTypeAsReserved(klass, reserved_klasses) from this module in
place of Archetypes' registerType().

A reserver class must subclass the ReserverMixin class from this
module and must call either registerTypeAsReserver(klass,
reserved_klasses) or registerTypeAsReserved(klass, reserved_klasses)
from this module in place of Archetypes' registerType().  The
ReserverMixin class subclasses Archetypes' BaseFolder class.

In both registerTypeAsReserver() and registerTypeAsReserver()
reserved_klasses should be a sequence of actual classes.

ReservedTypes handles the default values for the schema defined in
reservee classes.  It also handles the wildly different approaches
between vanilla CMF and Plone to id generation.  If your Archetype has
its own constructors, be sure those constructors return the apropriate
id, preferrably from klass.id.  It also sets meta_types (if defined).

It also checks for the res_before and res_after attributes and handles
the OrderedFolder interface based upon them.  They should be tuples of
either classes or strings.  If an item is a class, the object will be
instantiated before and after all existing objects that have that
class as a base class.  If an item is a string, the same will be done
for existing objects that have that id.  If res_after is set, then it
takes precedence, which is to say the object will be put immediately
after the last object in res_after rather than immediately before the
last object in res_before.  Set both res_after and res_before if you
want error checking for your ordered reserved types, as errors will be
raised if res_after and res_before result in ambiguity.  """

# Look into isConstructionAllowed for a better hook for reservees,
# maybe we can limit which types show up in allowedContentTypes()
# without modifying the container object's class.

from sys import modules
from types import StringType, ClassType

from DocumentTemplate.sequence import sort
from OFS.ObjectManager import BadRequestException
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ExtensionClass import Base
from Interface.IInterface import IInterface

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import registerType, Schema
from Products.Archetypes.public import DisplayList
from Products.Archetypes.ArchetypeTool import generateCtor
from Products.Archetypes.Widget import IdWidget
from Products.Archetypes.OrderedBaseFolder import OrderedBaseFolder

from Products.InheritanceUtils import implementsValues

def processReserver(klass, reserved_klasses):
    ids = {}
    types = {}
    type_titles = ()

    for k in reserved_klasses:
        id = k.id
        type = k.__name__
        
        ids[id] = type
        types[type] = id
        type_titles += (k.archetype_name,)

    ck = klass
    ck._res_ids = ids
    ck._res_types = types
    ck.allowed_content_types = tuple(types.keys()) + ck.allowed_content_types
    meta_types = getattr(ck, 'meta_types', ())
    if meta_types: meta_types = type_titles + meta_types

def processReservee(klass):
    k = klass
    module = modules[k.__module__]
    type = k.__name__
    k.schema = k.schema.copy()
    si, st = k.schema['id'], k.schema['title']
    si.default = k.id
    si.vocabulary = DisplayList([(k.id, k.id)])
    si.enforcevocabulary = 1
    si.widget.visible = {'edit':'hidden',
                         'view':'invisible'}
    st.default = k.title
    st.vocabulary = DisplayList([(k.title, k.title)])
    st.enforcevocabulary = 1
    st.widget.visible = {'edit':'hidden',
                         'view':'invisible'}

def registerTypeAsReserver(klass, reserved_klasses):
    processReserver(klass, reserved_klasses)
    return registerType(klass)

def registerTypeAsReservee(klass):
    processReservee(klass)
    return registerType(klass)

def registerTypeAsReserved(klass, reserved_klasses):
    processReservee(klass)
    return registerTypeAsReserver(klass, reserved_klasses)

def contentValuesByIds(self, ids):
    """Return a list of content objects whose id is in the given
    sequence.  Should be added as a class method if needed."""
    return [v for v in self.contentValues() if v.getId() in ids]

seq_types = (type(()), type([]))

def funcGroupValues(container, func, *args):
    if len(args) == 1 and type(args[0]) in seq_types: args = args[0]
    return func(container, args)

def slotValues(container, *func_groups):
    if callable(func_groups[0]): func_groups = (func_groups,)
    results = []
    for func_group in func_groups:
        results += funcGroupValues(container, func_group[0],
                                   *func_group[1:])
    return results

strict_errors = {
    'one_slot':
    'The item created (%s) apeared in multiple slots: %s',
    }

def resolveSpec(container, oidx, spec, strict=()):
    #if (len(spec) == 1 and
    #    ((len(spec[0]) == 1 and callable(spec[0][0]))
    #     or callable(spec[0]))): spec = spec[0]
    if callable(spec[0]): spec = (spec,)
    results = []
    processed = []
    for slot in spec:
        idxs = []
        for v in slotValues(container, *slot):
            idx = container.getObjectPosition(v.getId())
            # We only want indexes for the earliest slot it appears in
            if idx not in processed:
                idxs.append(idx)
                processed.append(idx)
            elif 'one_slot' in strict and oidx == idx:
                raise ValueError, strict_errors['one_slot'] % (oidx,
                                                               slot)
        results.append(idxs)
    # add all remaining indexes not names in the spec at the end
    results.append([idx for idx in
                    range(len(container.contentValues()))
                    if idx not in processed])
    return results

def flatten(*seq):
    results = []
    for item in seq:
        if type(item) in seq_types: results += flatten(*item)
        else: results.append(item)
    return results
    
def getIdxForObject(container, id, spec, strict=()):
    oidx = container.getObjectPosition(id)
    slots = resolveSpec(container, oidx, spec, strict)
    # object is in last slot, shouldn't be moved
    if oidx in slots[-1]: return
    # eliminate slots before slot containing object
    while slots:
        if oidx in slots.pop(0): break
    # object found, return the lowest index from the trailing slots
    idxs = flatten(slots)
    idxs.sort()
    if idxs: return idxs[0]
    
class ReserverMixin(Base):

    def getNonReserver(self):
        # moves up the containment tree looking for a non-reserver
        # parent
        p = self.getParentNode()
        pr = getattr(p, 'getNonReserver', None)
        if pr: return pr()
        else: return p

    def generateUniqueId(self, type_name=None):
        # hook Plone's automatic id generation
        # this has to be a method cause it has to run unprotected
        # python
        res_types = getattr(self, '_res_types', None)
        # time for acquisition voodoo for the fallback, here we
        # get the generateUniqueId from a non-reserver but we
        # specify that self will acquire it so that it will act on
        # self, not on the non-reserver we got it from
        NR_generateUniqueId = self.getNonReserver(
            ).generateUniqueId.__of__(self)
        if not res_types: return NR_generateUniqueId(type_name)
        id = self._res_types.get(type_name, '')
        if id: return id
        return NR_generateUniqueId(type_name)

    def allowedContentTypes(self):
        """
        List type info objects for types which can be added in
        this folder.

        Modified to check for reserved types.
        """
        return self.filterReservedTypes(
            OrderedBaseFolder.allowedContentTypes(self))

    def filterReservedTypes(self, types):
        # use getattr to allow non reserver types to pass without
        # fail, may want to rethink this and mandate that only actual
        # reservers can subclass this without error.
        results = types
        tt = getToolByName(self, 'portal_types')
        for tn in getattr(self, '_res_types', {}).keys():
            t = tt.getTypeInfo(tn)
            if self.objectValues([tn,]) and t in results:
                results.remove(t)
        return results

    def checkIdReserved(self, id):
        return id in getattr(self, '_res_ids', {}).keys()

    def checkReservedValid(self, id, object):
        return not (self.checkIdReserved(id) and
                    self._res_ids[id] != object.meta_type)

    def checkIdAvailable(self, id):
        # For validation
        # doesn't seem to catch for the rename form
        if not self.checkIdReserved(id):
            return OrderedBaseFolder.checkIdAvailable(self, id)

    # It gets weird here.  I want to meaningfully enforce reserved
    # ids.  So I override _setObject, but if any error is raised in
    # _setObject when it is called in manage_renameObject then the
    # object disappears from the container.  So I override
    # manage_renameObject too.
    def _setObject(self,id,object, *args, **kw):
        if self.checkReservedValid(id, object):
            return OrderedBaseFolder._setObject(self, id, object,
                                         *args, **kw)
        raise BadRequestException, ('The id "%s" is reserved.'
                                    % new_id)

    def manage_renameObject(self, id, new_id, *args, **kw):
        """ Override CopySupport.manage_renameObject """
        if self.checkReservedValid(new_id, getattr(self, id)):
            return OrderedBaseFolder.manage_renameObject(self, id, new_id,
                                                  *args, **kw)
        raise BadRequestException, ('The id "%s" is reserved.'
                                    % new_id)

    implementsValues = implementsValues

    def moveNewObject(self, id):
        object = self.contentValues()[-1]
        oid = object.getId()
        if oid != id:
            raise ValueError, ('The last object in %s is %s.  It '
                               'should be %s.'
                               % (self.getId(), oid, id))
        res_order = getattr(self, 'res_order', None)
        if res_order:
            tidx = getIdxForObject(self, id, res_order)
            if tidx != None: self.moveObject(id, tidx)

    def invokeFactory(self, type_name, id, RESPONSE=None, *args,
                      **kw):
        """Overridden to catch creation of subobjects."""
        new_id = OrderedBaseFolder.invokeFactory(self, type_name, id,
                                                 RESPONSE, *args,
                                                 **kw) or id
        self.moveNewObject(new_id)
        return new_id

def getIndexesFromSpec(container, spec):
    results = []
    if type(spec[0]) not in seq_types: spec = (spec,)
    for func, arg in spec:
        results += func(container, arg)
    results = [container.getObjectPosition(o.getId())
               for o in results]
    results.sort()
    return results
    
class ReservedMixin:

    def getOrderIndexes(self, seq):
        p = self.getParentNode()
        res = []
        # give this flex argument bs up and go with type strings
        for item in seq:
            if type(item) == type(IInterface):
                res += p.implementsValues([item])
            # Should really use interfaces only for this but they're
            # not consitently used (Document)
            elif type(item) == ClassType:
                res += p.classValues([item.__name__])
            # if its a string, its an id
            elif type(item) == StringType:
                res += p.classValues([item])
            else:
                raise TypeError, ('%s is not a type, interface or'
                                    ' class.' % item)
        res = [p.getObjectPosition(o.getId()) for o in res]
        res.sort()
        return res
    
    def initializeArchetype(self, **kwargs):
        # Handle ordered reserved types.
        order = {}
        p = self.getParentNode()
        # a spec is assembled for allowed types and is put into before
        allowed_spec = (p.contentValues,
                        getattr(self, 'allowed_content_types', ()))
        b_spec = getattr(self.aq_base, 'res_before', ())
        a_spec = getattr(self.aq_base, 'res_after', ())
        # First get two lists of objects to go before and after self
        b = getIndexesFromSpec(p, b_spec + (allowed_spec,))
        a = getIndexesFromSpec(p, a_spec)
        id = self.getId()
        if a and b and a[-1] >= b[0]:
            objs = p.objectValues()
            errs = [objs[i].absolute_url() for i in b if i >= a[0]]
            raise AttributeError, ('The following objects are ' +
                                   'listed in both the ' +
                                   'res_before and res_after '+
                                   'attributes of %s: %s' %
                                   (self.absolute_url(), errs))
        elif a: p.moveObject(id, a[-1]+1)
        elif b: p.moveObject(id, b[0]-1)
        
        return

