import types
import AccessControl.User
#import base64

from Products.CMFMember import MemberPermissions
from Products.CMFMember.MemberPermissions import VIEW_PUBLIC_PERMISSION, EDIT_ID_PERMISSION, \
    EDIT_REGISTRATION_PERMISSION, VIEW_OTHER_PERMISSION, EDIT_OTHER_PERMISSION, \
    VIEW_SECURITY_PERMISSION, EDIT_PASSWORD_PERMISSION, EDIT_SECURITY_PERMISSION, \
    MAIL_PASSWORD_PERMISSION

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent, aq_base, aq_chain
from Products.CMFCore.interfaces.portal_memberdata import MemberData as IMemberData
from Products.CMFCore.utils import getToolByName, _limitGrantedRoles, _verifyActionPermissions
from Products.Archetypes import registerType
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.Archetypes.Field       import *
from Products.Archetypes.Widget      import *
from Products.Archetypes.debug import log
from DateTime import DateTime

from Products.CMFMember.Extensions.Workflow import triggerAutomaticTransitions

def modify_fti(fti):
    fti['global_allow'] = 0  # only allow Members to be added where explicitly allowed

content_schema = FieldList((
    StringField('id',
                required=1,
                accessor="getId",
                mutator="setId",
                mode='rw',
                read_permission=VIEW_PUBLIC_PERMISSION,
                write_permission=EDIT_ID_PERMISSION,
                default=None,
                widget=IdWidget(label_msgid="label_name",
                                description_msgid="help_name",
                                i18n_domain="plone"),
                ),

    StringField('fullname',
                default='',
                mode='rw',
                read_permission=VIEW_PUBLIC_PERMISSION,
                write_permission=EDIT_REGISTRATION_PERMISSION,
                searchable=1,
                widget=StringWidget(label='Full name',
                                    description='Enter your full name here.',)
                ),

    ObjectField('email',
                required=1,
                mode='rw',
                read_permission=VIEW_PUBLIC_PERMISSION,
                write_permission=EDIT_REGISTRATION_PERMISSION,
                searchable=1,
                widget=StringWidget(label='E-mail',
                                    description='Enter your e-mail address here.',)
                ),
    
    ObjectField('wysiwyg_editor',
                mode='rw',
                read_permission=VIEW_OTHER_PERMISSION,
                write_permission=EDIT_OTHER_PERMISSION,
                vocabulary='editors',
                enforceVocabulary=1,
                widget=SelectionWidget(format='flex',
                                       label='Content editor',
                                       description='Select the editor that you would like to use ' + \
                                                   'for editing content more easily. Content editors ' + \
                                                   'often have specific browser requirements.')
                ),
    
    ObjectField('formtooltips',
                 default=1,
                 mode='rw',
                 read_permission=VIEW_OTHER_PERMISSION,
                 write_permission=EDIT_OTHER_PERMISSION,
                 searchable=0,
                 widget=BooleanWidget(label='Form help',
                                      description='Indicate whether you want the form help pop-ups to be displayed.')
                ),

    ObjectField('visible_ids',
                default=1,
                mode='rw',
                read_permission=VIEW_OTHER_PERMISSION,
                write_permission=EDIT_OTHER_PERMISSION,
                widget=BooleanWidget(label='Display names',
                                     description='Indicate whether you want Names (also known as IDs) to be ' + \
                                                 'visible and editable when editing contents. If you choose not ' + \
                                                 'to display Names, they will be generated automatically.')
                ),

    ObjectField('portal_skin',
                mode='rw',
                read_permission=VIEW_OTHER_PERMISSION,
                write_permission=EDIT_OTHER_PERMISSION,
                required=1,
                searchable=0,
                vocabulary='available_skins',
                enforceVocabulary=1,
                widget=SelectionWidget(format='flex',
                                       label='Look',
                                       description='Choose the appearance of the site. Several styles are available.')
                ),

    ImageField('portrait',
               mode='rw',
               read_permission=VIEW_PUBLIC_PERMISSION,
               write_permission=EDIT_OTHER_PERMISSION,
               required=0,
               searchable=0,
               widget=ImageWidget(label='Portrait',
                                  description='To add a new portrait, click the <strong>Browse</strong> button and select ' + \
                                            'a picture of yourself. Recommended size is 75 pixels wide, 100 pixels tall)')
               ),
    
    StringField('password',
                default=None,
                mutator='_setPassword',
                accessor='_getPassword',
                mode='w',
                read_permission=VIEW_SECURITY_PERMISSION,
                write_permission=EDIT_PASSWORD_PERMISSION,
                searchable=0,
                widget=PasswordWidget(label='Password',
                                      description='Enter a new password (leave blank to keep your current password)')
                ),

    StringField('confirm_password',
                mutator='_setPassword',
                accessor='_getPassword',
                mode='w',
                read_permission=VIEW_SECURITY_PERMISSION,
                write_permission=EDIT_PASSWORD_PERMISSION,
                searchable=0,
                widget=PasswordWidget(label='Confirm password',
                                      description='Confirm your new password')
                ),

    LinesField('roles',
               default=('Member',),
               mutator='setRoles',
               accessor='getRoles',
               vocabulary='valid_roles',
               enforceVocabulary=1,
               multiValued=1,
               mode='rw',
               read_permission=VIEW_SECURITY_PERMISSION,
               write_permission=EDIT_SECURITY_PERMISSION,
               searchable=0,
               widget=MultiSelectionWidget(label='Roles',
                                           description='Select the security roles for this user')
               ), 
    
    LinesField('domains',
               default=(),
               mutator='setDomains',
               accessor='getDomains',
               mode='rw',
               read_permission=VIEW_SECURITY_PERMISSION,
               write_permission=EDIT_SECURITY_PERMISSION,
               searchable=0,
               widget=LinesWidget(label='Domains',
                                  description='If you would like to restrict this user to logging in only from certain domains, enter those domains here.')
               ),

    DateTimeField('login_time',
                  default='2000/01/01',  # for Plone 1.0.1 compatibility
                  mode='r',
                  read_permission=VIEW_OTHER_PERMISSION,
                  write_permission=EDIT_OTHER_PERMISSION,
                  searchable=0,
                  widget=StringWidget(label="Login time",
                                      visible=-1,)),
    
    DateTimeField('last_login_time',
                  default='2000/01/01',  # for Plone 1.0.1 compatibility
                  mode='r',
                  read_permission=VIEW_OTHER_PERMISSION,
                  write_permission=EDIT_OTHER_PERMISSION,
                  searchable=0,
                  widget=StringWidget(label="Last login time",
                                      visible=-1,)),
    ))

_marker = []

class Member(BaseContent):
    """A description of a member"""
    __implements__ = IMemberData, IBaseContent

    security = ClassSecurityInfo()

    portal_type = meta_type = "Member"

    # Note that we override BaseContent.schema
    schema = content_schema + ExtensibleMetadata.schema
    listed = 0

    ##IMPL DETAILS
    def __init__(self, userid):
        BaseContent.__init__(self, userid)
        self.id = str(userid)
        self._setPassword(self.generatePassword())
        self.listed = 0


    def view(self, **kwargs):
        return self.getTypeInfo().getActions()
        for action in actions:
            if action.get('id', None) == 'view':
                if _verifyActionPermissions(obj, action):
                    action = obj.restrictedTraverse(action['action'])
                    if action is not None:
                        return action(**kwargs)
        raise 'Unauthorized', ('No accessible views available for %s' %
                               '/'.join(self.getPhysicalPath()))


    security.declarePublic('getMemberId')
    def getMemberId(self):
        return self.getUserName()


    # ###############################
    # Validators

    security.declarePrivate('validate_id')
    def validate_id(self, id):
        # no change -- ignore
        if self.id and id == self.id:
            return None
        
        registration_tool = getToolByName(self, 'portal_registration')
        if registration_tool.isMemberIdAllowed(id):
            return None
        else:
            return 'The login name you selected is already ' + \
                   'in use or is not valid. Please choose another.'

    
    security.declarePrivate('validate_password')
    def validate_password(self, password):
        # no change -- ignore
        if not password:
            return None

        registration_tool = getToolByName(self, 'portal_registration')
        return registration_tool.testPasswordValidity(password)


    security.declarePrivate('validate_roles')
    def validate_roles(self, roles):
        roles = self._stringToList(roles)
        valid = self.valid_roles()
        for r in roles:
            if r not in valid:
                return '%s is not a valid role.' % (r)
        return None


    security.declarePrivate('post_validate')
    def post_validate(self, REQUEST, errors):
        if not(errors.get('password', None)) and not(errors.get('confirm_password', None)):
            if REQUEST.get('password', None) != REQUEST.get('confirm_password', None):
                errors['password'] = errors['confirm_password'] = \
                    'Your password and confirmation did not match. ' \
                     + 'Please try again.'


    def isValid(self):
        import sys
        sys.stdout.write('isValid\n')
        errors = {}
        # make sure object has required data and metadata
        self.Schema().validate(self, None, errors, 1, 1)
        if errors:
            return 0
        return 1

    # ###############################
    # Contract with portal_membership
    
    security.declareProtected(MemberPermissions.EDIT_OTHER_PERMISSION, 'setProperties')
    def setProperties(self, mapping=None, **kwargs):
        """assign all the props to member attributes, we expect
        to be able to find a mutator for each of these props
        """
        #We know this is an Archetypes based object so we look for
        #mutators there first

        # if mapping is not a dict, assume it is REQUEST
        if mapping:
            if not type(mapping) == type({}):
                data = {}
                for k,v in mapping.form.items():
                    data[k] = v
                mapping = data
        else:
            mapping = {}

        if kwargs:
            # mapping could be a request object thats not really a dict,
            # this is what we get
            mapping.update(kwargs)

        self.update(**mapping)


    security.declarePrivate('setMemberProperties')
    def setMemberProperties(self, mapping):
        self.setProperties(mapping)


    security.declarePublic('getProperty')
    def getProperty(self, id, default=_marker):
        #assume Archetypes attr here 
        accessor = getattr(self, self.schema[id].accessor, None)
        try:
            value = accessor()
        except:
            if default is _marker:
                # member does not have a value for given property
                # try memberdata_tool for default value
                memberdata_tool = getToolByName(self, 'portal_memberdata')
                try:
                    value = memberdata_tool.getProperty(id)
                except:
                    raise AttributeError(id)
            else:
                value = default

        return value


    security.declarePublic('getUser')
    # XXX is this perm correct?
    def getUser(self):
        if not hasattr(self, '_v_user'):
            u = self.acl_users.getUser(self.id)
            if u is not None:
                self._v_user = u
            else:
                # create a temporary user - turn into a real user when register() is called
                self._v_user = AccessControl.User.SimpleUser(self.id, self.password, self.roles, self.domains)
        return aq_base(self._v_user).__of__(self.acl_users) # restore the proper context


    # ###############################
    # Overrides of base class mutators that trigger workflow transitions
    
    def update(self, **kwargs):
        ret = BaseContent.update(self, **kwargs)
        # invoke any automated workflow transitions after update
        import sys
        sys.stdout.write('update\n')
        triggerAutomaticTransitions(self)
        return ret


    def processForm(self, data=1, metadata=0):
        ret = BaseContent.processForm(self, data, metadata)
        # invoke any automated workflow transitions after update
        import sys
        sys.stdout.write('processForm\n')
        triggerAutomaticTransitions(self)
        return ret


    # ###############################
    # Methods triggered by workflow transitions

    security.declarePrivate('register')
    def register(self):
        import sys
        sys.stdout.write('registering\n')
        registration_tool = getToolByName(self, 'portal_registration')
        user_created = 0
        # create a real user
        if self.acl_users.getUser(self.id) is None:
            # Limit the granted roles.
            # Anyone is always allowed to grant the 'Member' role.
            roles = self.getRoles()
            _limitGrantedRoles(roles, self, ('Member',))

            self.acl_users.userFolderAddUser(self.id, self._getPassword(), roles, self.getDomains())
            self._v_user = self.acl_users.getUser(self.id)
            user_created = 1

        # make the user the owner of the current member object
        sys.stdout.write('registering: changeOwnership\n')
        self.changeOwnership(self.getUser(), 1)
        sys.stdout.write('registering: afterAdd\n')
        # XXX - should we invoke this for members with users in the Zope root acl_user?
        registration_tool.afterAdd(self, id, self._getPassword(), None)
        sys.stdout.write('registering: updateListed\n')
        self.updateListed()

        # only send mail if we had to create a new user -- this avoids
        # sending mail to users who are already registered at the Zope root level
        if user_created:
            sys.stdout.write('registering: registeredNotify\n')
            registration_tool.registeredNotify(self.getUserName())
        sys.stdout.write('registering: done\n')


    security.declarePrivate('disable')
    def disable(self):
        self._setPassword(self.generatePassword())
        self.listed = 0


    security.declarePrivate('disable')
    def updateListed(self):
        """Extract the correct value of the Member's 'listed' attribute from
           current security settings."""
        membership_tool = getToolByName(self, 'portal_membership')
        self.listed = membership_tool.checkPermission(VIEW_PUBLIC_PERMISSION, self)


    # ###############################

    security.declareProtected(MemberPermissions.EDIT_ID_PERMISSION, 'setId')
    def setId(self, id):
        if hasattr(self, '_v_user'):
            old_user_id = self._v_user.getUserName()
            # if a user with with id old_user_id exists, recurse through
            # the portal and modify local roles and ownership
            portal = getToolByName(self, 'portal_url').getPortalObject()
            if self.acl_users.getUser(old_user_id) is not None:
                # delete local roles and content owned by this user
                self._changeUserInfo(portal, old_user_id, id)
                # create a new user with the appropriate id
                self.acl_users.userFolderAddUser(id, self._getPassword(), self.getRoles(), self.getDomains())
                # delete the old user
                self.acl_users.userFolderDelUsers((old_user_id,))
            delattr(self, '_v_user')

        memberdata=getToolByName(self, 'portal_memberdata')
        memberdata.manage_renameObjects( (self.getId(),), (id,) )

    security.declarePrivate('setUser')
    def setUser(self, user):
        # XXX -- make sure the right things happen if
        # the new user has a different id than the current user
        assert(user.getUserName() == self.id)
        self._v_user = user


    ##USER INTERFACE IMPL
    security.declarePublic('Title')
    def Title(self):
        return self.id


    security.declarePublic('getUserName')
    def getUserName(self):
        """Return the username of a user"""
        return self.getUser().getUserName()


    security.declarePrivate('_getPassword')
    def _getPassword(self):
        """Return the password of the user."""
        return self.getUser()._getPassword()


    security.declarePrivate('getRoles')
    def getRoles(self):
        """Return the list of roles assigned to a user."""
        roles=()
        try:
            roles=self.getUser().getRoles()
        except TypeError:
            #XXX The user is not in this acl_users so we get None
            if self.getUser().roles is None:
                self.getUser().roles=('Member',)
            roles=self.getUser().getRoles()
        # filter out Authenticated, etc
        allowed = self.valid_roles()
        return tuple([r for r in roles if r in allowed])


    security.declarePrivate('getDomains')
    def getDomains(self):
        """Return the list of domain restrictions for a user"""
        domains=()
        try:
            domains=self.getUser().getDomains()
        except TypeError:
            if self.getUser().domains is None:
                self.getUser().domains=()
            domains=self.getUser().getDomains()
        return domains


    def _setPassword(self, password):
        if password:
            self.getUser().__ = password
            # don't log out the current user
            if self.REQUEST:
                membership_tool = getToolByName(self, 'portal_membership')
                if membership_tool.getAuthenticatedMember().getUserName() == self.getUserName():
                    # XXX make sure this works -- replaces commented out code below
                    cookie_crumbler = getToolByName(self, 'cookie_crumbler')
                    cookie_crumbler.credentialsChanged(self.getUser(), self.getUserName(), password)
#                    # XXX - this is kind of ugly -- is there a better way?
#                    token = self.getUserName() + ':' + password
#                    token = base64.encodestring(token)
#                    token = quote(token)
#                    self.REQUEST.response.setCookie('__ac', token, path='/')
#                    self.REQUEST['__ac']=token


    def _stringToList(self, s):
        # XXX May not need this anymoure
        if s is None:
            return []
        if isinstance(s, types.StringType):
            # split on , or \n and ignore \r
            s = s.replace('\r','')
            s = s.replace('\n',',')
            s = s.split(',')
            s= [v.strip() for v in s if v.strip()]
            s = filter(None, s)
        return s


    security.declarePrivate('setRoles')
    def setRoles(self, value):
        value = self._stringToList(value)
        self.getUser().roles = value


    security.declarePrivate('setDomains')
    def setDomains(self, value):
        value = self._stringToList(value)
        self.getUser().domains = value

    
    security.declarePrivate('setSecurityProfile')
    def setSecurityProfile(self, password=None, roles=None, domains=None):
        """Set the user's basic security profile"""
        if password is not None:
            self._setPassword(password)
        if roles is not None:
            self.setRoles(roles)
        if domains is not None:
            self.setDomains(domains)


    #Vocab methods
    def editors(self):
        return self.portal_properties.site_properties.available_editors

    def valid_roles(self):
        roles = list(self.getUser().valid_roles())
        # remove automatically added roles
        if 'Authenticated' in roles:
            roles.remove('Authenticated')
        if 'Anonymous' in roles:
            roles.remove('Anonymous')
        return tuple(roles)

    def available_skins(self):
        return self.portal_skins.getSkinSelections()

    ##
    def __str__(self):
        return self.id

    
    def __call__(self, *args, **kwargs):
        return self.id


    # ###########################
    def generatePassword(self):
        try:
            registration_tool = getToolByName(self, 'portal_registration')
            return registration_tool.generatePassword()
        except AttributeError:
            # during migration we generate Member objects that don't have
            # access to the portal -- punt
            return None

    # replacement for portal_registration's mailPassword function
    security.declareProtected(MAIL_PASSWORD_PERMISSION, 'mailPassword')
    def mailPassword(self):
        """ Email a forgotten password to a member."""
        # assert that we can actually get an email address, otherwise
        # the template will be made with a blank To:, this is bad
        if not member.getProperty('email'):
            raise 'ValueError', 'Member does not have an email address.'
        
        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        mail_text = self.mail_password_template( self
                                               , self.REQUEST
                                               , member=self
                                               , password=self._getPassword()
                                               )
        host = self.MailHost
        host.send( mail_text )
        return self.mail_password_response( self, REQUEST )


    # ###########################
    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        BaseContent.manage_beforeDelete(self, item, container)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        # make sure the user with id old_user_id exists before recursing through
        # the whole portal
        if self.acl_users.getUser(self.id) is not None:
            # delete local roles and content owned by this user
            self._changeUserInfo(portal, self.id)
            self.acl_users.userFolderDelUsers((self.id,))


    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self):
        BaseContent.manage_afterClone(self)
        # Remove the link to the old object's user
        # _v_user will be lazily regenerated
        delattr(self, '_v_user')


    # utility method for altering information related to a user
    # when a member is renamed or deleted
    def _changeUserInfo(self, context, old_user_id, new_user_id=None):
        # remove any local roles the user may have had
        if context.isPrincipiaFolderish:
            for o in context.objectValues():
                if self._changeUserInfo(o, old_user_id, new_user_id):
                    # delete object if need be
                    context.manage_delObjects((o.getId(),))
                    
            if new_user_id is not None:
                # transfer local roles for old user to local roles for new user
                roles = context.get_local_roles_for_userid(old_user_id)
                if roles:
                    context.manage_addLocalRoles(new_user_id, roles)
                context.manage_delLocalRoles(old_user_id)
            else:
                # delete local roles for old user
                context.manage_delLocalRoles(old_user_id)

        # if this object is owned by the user that is being deleted,
        # either change its ownership to new_owner or mark it for deletion
        owner = context.getOwner(1)
        if owner == old_user_id:
            if new_user_id is not None:
                context.changeOwnership(new_user_id)
            else:
                # mark this object for deletion
                return 1
        return 0




    # XXX REFACTOR ME
    # This is used for a hack in MemberDataTool
    def _getTypeName(self):
        return 'CMFMember Content'

registerType(Member)
