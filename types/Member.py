import types
import AccessControl.User

from Products.CMFMember import MemberPermissions
from Products.CMFMember.MemberPermissions import VIEW_PUBLIC_PERMISSION, EDIT_ID_PERMISSION, \
    EDIT_REGISTRATION_PERMISSION, VIEW_OTHER_PERMISSION, EDIT_OTHER_PERMISSION, \
    VIEW_SECURITY_PERMISSION, EDIT_PASSWORD_PERMISSION, EDIT_SECURITY_PERMISSION, \
    MAIL_PASSWORD_PERMISSION

from AccessControl import ClassSecurityInfo, Owned
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
                index='FieldIndex|schema',
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
                index='TextIndex|schema',
                widget=StringWidget(label='Full name',
                                    description='Enter your full name here.',)
                ),

    ObjectField('email',
                required=1,
                mode='rw',
                read_permission=VIEW_PUBLIC_PERMISSION,
                write_permission=EDIT_REGISTRATION_PERMISSION,
                validators=('isEmail',),
                index='FieldIndex|schema',
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
                vocabulary='available_skins',
                enforceVocabulary=1,
                searchable=0,
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
                mutator='_setConfirmPassword',
                accessor='_getConfirmPassword',
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
               mode='rw',
               read_permission=VIEW_SECURITY_PERMISSION,
               write_permission=EDIT_SECURITY_PERMISSION,
               vocabulary='valid_roles',
#               enforceVocabulary=1, # don't enforce vocabulary because getRoles() adds some extra roles
               multiValued=1,
               searchable=0,
               index='KeywordIndex',
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
               multivalued=1,
               searchable=0,
               index='KeywordIndex',
               widget=LinesWidget(label='Domains',
                                  description='If you would like to restrict this user to logging in only from certain domains, enter those domains here.')
               ),

#    DateTimeField('login_time',
#                  default='2000/01/01',  # for Plone 1.0.1 compatibility
#                  mode='r',
#                  read_permission=VIEW_OTHER_PERMISSION,
#                  write_permission=EDIT_OTHER_PERMISSION,
#                  searchable=0,
#                  widget=StringWidget(label="Login time",
#                                      visible=-1,)),
#    
#    DateTimeField('last_login_time',
#                  default='2000/01/01',  # for Plone 1.0.1 compatibility
#                  mode='r',
#                  read_permission=VIEW_OTHER_PERMISSION,
#                  write_permission=EDIT_OTHER_PERMISSION,
#                  searchable=0,
#                  widget=StringWidget(label="Last login time",
#                                      visible=-1,)),
    ))

_marker = []

class Member(BaseContent):
    """A description of a member"""
    __implements__ = IMemberData, IBaseContent

    security = ClassSecurityInfo()

    portal_type = meta_type = "Member"

    # Note that we override BaseContent.schema
    schema = content_schema + ExtensibleMetadata.schema

    # for Plone compatibility -- managed by workflow state
    listed = 0
    login_time = '2000/01/01'
    last_login_time = '2000/01/01/'
    
    # the user folder containing the user associated with this member
    _userFolder = None
    _user = None


    ##IMPL DETAILS
    def __init__(self, userid):
        BaseContent.__init__(self, userid)
        self.id = str(userid)
        self.password = None
        self.roles = None
        self.domains = None
        self._setPassword(self._generatePassword())
        self._userFolder = None
        self._createUser()
        # for plone compatibility
        self.listed = 0
        self.login_time = '2000/01/01'
        self.last_login_time = '2000/01/01'


    def view(self, **kwargs):
        """View action"""
        actions = self.getTypeInfo().getActions()
        for action in actions:
            if action.get('id', None) == 'view':
                if _verifyActionPermissions(self, action):
                    action = self.restrictedTraverse(action['action'])
                    import sys
                    sys.stdout.write('action = %s\n' % str(action))
                    if action is not None:
                        return action(**kwargs)
        raise 'Unauthorized', ('No accessible views available for %s' %
                               '/'.join(self.getPhysicalPath()))


    def __str__(self):
        return self.id

    
    def __call__(self, *args, **kwargs):
        return self.id


    # ########################################################################
    # User interface
    security.declarePublic('Title')
    def Title(self):
        return self.id


    security.declarePublic('getUserName')
    def getUserName(self):
        """Return the username of a user"""
        return self.getUser().getUserName()


    security.declareProtected(VIEW_PUBLIC_PERMISSION, 'getPortrait')
    def getPortrait(self):
        """Return a member's portrait using the Plone portal_membership methods."""
        membership_tool = getToolByName(self, 'portal_membership')
        return membership_tool.getPersonalPortrait(self.getId(), 1)


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
        return roles
#        # filter out Authenticated, etc
#        allowed = self.valid_roles()
#        return tuple([r for r in roles if r in allowed])


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


    # dummy method
    security.declarePrivate('_setConfirmPassword')
    def _setConfirmPassword(self, value):
        pass


    # dummy method
    security.declarePrivate('_getConfirmPassword')
    def _getConfirmPassword(self):
        return ''


    def _setPassword(self, password):
        if password:
            self.password = password
            self.setSecurityProfile(password=password)


    security.declarePrivate('setRoles')
    def setRoles(self, roles):
        roles = self._stringToList(roles)
        self.roles = roles
        self.setSecurityProfile(roles=roles)


    security.declarePrivate('setDomains')
    def setDomains(self, domains):
        # get rid of empty string domains!
        domains = self._stringToList(domains)
        self.domains = domains
        self.setSecurityProfile(domains=domains)

    
    security.declarePrivate('setSecurityProfile')
    def setSecurityProfile(self, password=None, roles=None, domains=None):
        """Set the user's basic security profile"""
        if password is None:
            password = self.password
        if roles is None:
            roles = self.roles
        if domains is None:
            domains = self.domains

        if self._userFolder:
            # if our user lives in a user folder, do this the right way

            self.getUserFolder().userFolderEditUser(self.id, password, roles, domains)
        else:
            # we have a temporary user in hand -- set its attributes by hand
            self.getUser().__ = password
            self.getUser().roles = roles
            self.getUser().domains = domains

    # ########################################################################
    # Validators and vocabulary methods

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
        valid = self.valid_roles() + ('Authenticated',)
        for r in roles:
            if r not in valid:
                return '%s is not a valid role.' % (r)
        return None


    security.declarePrivate('post_validate')
    def post_validate(self, REQUEST, errors):
        if REQUEST and not(errors.get('password', None)) and not(errors.get('confirm_password', None)):
            if REQUEST.get('password', None) != REQUEST.get('confirm_password', None):
                errors['password'] = errors['confirm_password'] = \
                    'Your password and confirmation did not match. ' \
                     + 'Please try again.'


    def isValid(self):
        errors = {}
        # make sure object has required data and metadata
        self.Schema().validate(self, None, errors, 1, 1)
        if errors:
            import sys
            sys.stdout.write('isValid, errors = %s\n' % (str(errors)))
            return 0
        return 1


    # Vocabulary methods
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

    # ########################################################################
    # Contract with portal_membership

    security.declarePublic('getMemberId')
    def getMemberId(self):
        """Get the member id """
        return self.getUserName()

    
    security.declareProtected(EDIT_OTHER_PERMISSION, 'setProperties')
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
    def getUser(self):
        if self._userFolder:
            # XXX should context be self.acl_users or self._userFolder?
            return aq_base(self.getUserFolder().getUser(self.id)).__of__(self.acl_users) # restore the proper context
        else:
            if self._user is None:
                self._createUser()
            return aq_base(self._user).__of__(self.acl_users) # restore the proper context


    # ########################################################################
    # Overrides of base class mutators that trigger workflow transitions
    
    def update(self, **kwargs):
        membership_tool = getToolByName(self, 'portal_membership')
        updateSelf = membership_tool.getAuthenticatedMember().getUserName() == self.getUserName()
        ret = BaseContent.update(self, **kwargs)
        if updateSelf:
            self._updateCredentials()
        # invoke any automated workflow transitions after update
        import sys
        sys.stdout.write('update\n')
        triggerAutomaticTransitions(self)
        return ret


    def processForm(self, data=1, metadata=0):
        membership_tool = getToolByName(self, 'portal_membership')
        updateSelf = membership_tool.getAuthenticatedMember().getUserName() == self.getUserName()
        ret = BaseContent.processForm(self, data, metadata)
        if updateSelf:
            self._updateCredentials()
        # invoke any automated workflow transitions after update
        import sys
        sys.stdout.write('processForm\n')
        triggerAutomaticTransitions(self)
        return ret


    # ########################################################################
    # Methods triggered by workflow transitions

    security.declarePrivate('register')
    def register(self):
        import sys
        sys.stdout.write('registering\n')
        registration_tool = getToolByName(self, 'portal_registration')
        user_created = 0
        # create a real user
        if self._userFolder is None:
            # Limit the granted roles.
            # Anyone is always allowed to grant the 'Member' role.
            roles = self.getRoles()
            _limitGrantedRoles(roles, self, ('Member',))
            self.setRoles(roles)
            self._createUser(force_create=1)
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
        self._setPassword(self._generatePassword())
        self.listed = 0


    security.declarePrivate('makePublic')
    def makePublic(self):
        self.listed = 1


    security.declarePrivate('makePrivate')
    def makePrivate(self):
        self.listed = 0


    # ########################################################################
    security.declareProtected(EDIT_ID_PERMISSION, 'setId')
    def setId(self, id):
        memberdata=getToolByName(self, 'portal_memberdata')
        memberdata.manage_renameObjects( (self.getId(),), (id,) )


    def _notifyOfCopyTo(self, container, op=0):
        Member.inheritedAttribute('_notifyOfCopyTo')(self, container, op)
        if op:
            self._v_old_id = self.id


    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, object, container):
        BaseContent.manage_afterAdd(self, object, container)
        assert(object is self)  # XXX - when would this not be true???

        old_id = getattr(self, '_v_old_id', None)
        if self.id == old_id:
            return

        if hasattr(self, '_v_old_id'):
            delattr(self, '_v_old_id')
            if self._userFolder:
                old_folder = self.getUserFolder()
                
                self._userFolder = [getToolByName(self, 'portal_url').getPortalObject().acl_users]
                self._createUser()
                # the old user was real -- transfer ownership and local roles to the new user
                portal = getToolByName(self, 'portal_url').getPortalObject()
                # change local roles and content ownership info
                old_user_folder = self._getUserFolderForUser(old_id)
                old_user = old_user_folder.getUser(old_id)
                old_owner_info = Owned.ownerInfo(old_user)
                new_owner = self.getUser().__of__(self.getUserFolder())
                self._changeUserInfo(portal, old_owner_info, new_owner)

                # delete the old user object if it is from portal.acl_users and not
                # from root.acl_users
                if old_folder == self.acl_users: 
                    # delete the old user
                    old_folder.userFolderDelUsers((old_id,))


    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self, object):
        if self._userFolder:
            self._userFolder = [getToolByName(self, 'portal_url').getPortalObject().acl_users]
        self._createUser()


    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        BaseContent.manage_beforeDelete(self, item, container)
        if hasattr(self, '_v_old_id'):
            # if we are in the midst of a move, do nothing
            return

        portal = getToolByName(self, 'portal_url').getPortalObject()

        # recurse through the portal and delete all of the user's content
        # XXX we should create some other options here
        # XXX Do we really want to delete the user's stuff if s/he isn't in
        #     the portal's acl_users folder?
        self._changeUserInfo(portal, Owned.ownerInfo(self.getUser().__of__(self.getUserFolder())))
        # delete the User object if it's in the current portal's acl_users folder
        if self.getUserFolder() == portal.acl_users:
            self.acl_users.userFolderDelUsers((self.id,))


    security.declarePrivate('setUser')
    def setUser(self, user):
        assert(user.getUserName() == self.id)
        self.password = user.__
        self.roles = user.roles
        self.domains = user.domains
        self._userFolder = [self._getUserFolderForUser(user.getUserName())]
        if self._userFolder is [None]:
            self._userFolder = None
            self._createUser()


    security.declarePrivate('_updateCredentials')
    def _updateCredentials(self):
        if self.REQUEST:
            # don't log out the current user
            if self._userFolder and hasattr(self.getUserFolder().aq_base, 'credentialsChanged'):
                # Use an interface provided by LoginManager.
                self.getUserFolder().credentialsChanged(self.getUser(), id, password)
            else:
                p = getattr(self.REQUEST, '_credentials_changed_path', None)
                if p is not None:
                    # Use an interface provided by CookieCrumbler.
                    change = self.restrictedTraverse(p)
                    change(self.getUser(), self.id, self._getPassword())


    security.declarePrivate('_createUser')
    def _createUser(self, force_create=0):
        if force_create and self._userFolder is None:
            self._userFolder = [getToolByName(self, 'portal_url').getPortalObject().acl_users]
        if self._userFolder is None:
            self._user = AccessControl.User.SimpleUser(self.id, self.password, self.roles, self.domains)
        else:
            if not self.getUserFolder().getUser(self.id):
                self.getUserFolder().userFolderAddUser(self.id, self.password, self.roles, self.domains)
                self._user = None


    # We keep the user folder in a list so that we don't destroy its acquisition context
    def getUserFolder(self):
        if self._userFolder:
            return self._userFolder[0]
        else:
            return None


    security.declarePrivate('_getUserFolderForUser')
    def _getUserFolderForUser(self, id=None):
        f = getToolByName(self, 'portal_url').getPortalObject()
        if id is None:
            return f.acl_users
        while 1:
            if not hasattr(f, 'objectIds'):
                return
            if 'acl_users' in f.objectIds():
                if hasattr(f.acl_users, 'getUser'):
                    user = f.acl_users.getUser(id)
                    if user is not None:
                        return f.acl_users
            if hasattr(f, 'getParentNode'):
                f = f.getParentNode()
            else:
                return None

    
    security.declarePrivate('_getUserById')
    def _getUserById(self, id):
        acl_users = self._getUserFolderForUser(id)
        if acl_users is None:
            return None
        return acl_users.getUser(id)


    # utility method for altering information related to a user
    # when a member is renamed or deleted
    def _changeUserInfo(self, context, old_user_info, new_user=None):
        old_user_id = old_user_info[1]
        if new_user:
            new_user_id = new_user.getUserName()
        else:
            new_user_id = None

        if context.isPrincipiaFolderish:
            for o in context.objectValues():
                if self._changeUserInfo(o, old_user_info, new_user):
                    # delete object if need be
                    if o != self:
                        import sys
                        sys.stdout.write('deleting %s - %s\n' % (str(o), repr(o)))
                        context.manage_delObjects([o.getId()])
                    
            # remove any local roles the user may have had
            if new_user_id is not None:
                # transfer local roles for old user to local roles for new user
                roles = context.get_local_roles_for_userid(old_user_id)
                if roles:
                    context.manage_addLocalRoles(new_user_id, roles)
                context.manage_delLocalRoles([old_user_id])
            else:
                # delete local roles for old user
                context.manage_delLocalRoles([old_user_id])

        # if this object is owned by the user that is being deleted,
        # either change its ownership to new_owner or mark it for deletion
        owner = context.getOwner(1)
        if owner == old_user_info:
            if new_user_id is not None:
                context.changeOwnership(new_user)
            else:
                # mark this object for deletion
                return 1
        return 0


    # ########################################################################
    security.declarePrivate('_generatePassword')
    def _generatePassword(self):
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


    # ########################################################################
    # utility methods

    def _stringToList(self, s):
        if s is None:
            return []
        if isinstance(s, types.StringType):
            # split on , or \n and ignore \r
            s = s.replace('\r',',')
            s = s.replace('\n',',')
            s = s.split(',')
        s= [v.strip() for v in s if v.strip()]
        s = filter(None, s)
        return s


    # XXX REFACTOR ME
    # This is used for a hack in MemberDataTool
    def _getTypeName(self):
        return 'CMFMember Content'


    # ########################################################################
    # Migration methods.  Used to migrate CMFCore member data to Member
    # objects or to migrate from from one type of member objects to another.
        
    def _migrate(self, old_member, out):
        """Set Member attributes using values from old_member"""
        fields = self.Schema().fields() + ['listed', 'last_login']
        for new_field in fields:
            if new_field.name not in ['password', 'roles', 'domains']: # fields managed by user object
                try:
                    value = self._migrateGetOldValue(old_member, new_field.name, out)
                    self._migrateSetNewValue(new_field.name, value, out)
                    print >> out, '%s.%s = %s' % (str(old_member.getMemberId()), new_field.name, str(value))
                except:
                    pass
        if member.__class__ == CMFCore.MemberDataTool.MemberData:
            membership_tool = getToolByName(self, 'portal_membership')
            membership_tool.getPersonalPortrait()
            
    def _migrateGetOldValue(self, old, id, out):
        """Try to get a value from an old member object using a variety of
        methods."""
        old_schema = getattr(old, 'Schema', None)
        if old_schema is not None:
            old_schema = old_schema()

        new_schema = self.Schema()

        if old_schema:
            old_field = old_schema.get(id, None)
            if old_field:
                accessor = getattr(old, old_field.accessor, None)
                if accessor is not None:
                    return accessor()
        new_field = new_schema.get(id)
        try:
            accessor = getattr(old, new_field.accessor)
            if callable(accessor):
                return accessor()
            return accessor
        except:
            pass
        
        try:
            return getattr(old_member, id)
        except:
            pass
        
        print >> out, 'Unable to get property %s from member %s\n' % (new_field.name, old.getMemberId())
        raise ValueError
    
        
    def _migrateSetNewValue(self, id, value, out):
        """Utility method for setting a Member attribute using a variety of methods"""
        new_schema = self.Schema()
        new_field = new_schema.get(id, None)
        if new_field:
            if new_field.mutator is not None:
                mutator = getattr(self, new_field.mutator)
                mutator(value)
                return
            if hasattr(self, id):
                setattr(self, id, value)
                return
            print >> out, 'Unable to set property %s from member %s\n' % (new_field.name, self.getMemberId())
            raise ValueError
        else:
            if hasattr(self, id):
                setattr(self, id, value)
                return
            print >> out, 'Unable to set property %s from member %s\n' % (id, self.getMemberId())
            raise ValueError

registerType(Member)