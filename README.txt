GroupUserFolder


(c)2002 Ingeniweb



(This is a structured-text formated file)



ABSTRACT

  GroupUserFolder is a kind of user folder that provides a special kind of user management.
  Some users are "flagged" as GROUP and then normal users will be able to belong to one or
  serveral groups.

STRUCTURE

  Group and "normal" User management is distinct. Here's a typical GroupUserFolder hierarchy::

     - acl_users (GroupUserFolder)
     |
     |-- Users (GroupUserFolder-related class)
     | |
     | |-- acl_users (UserFolder or derived class)
     |
     |-- Groups (GroupUserFolder-related class)
     | |
     | |-- acl_users (UserFolder or derived class)


  So, INSIDE the GroupUserFolder (or GRUF), there are 2 acl_users :

    - The one in the 'Users' object manages real users

    - The one in the 'Groups' object manages groups

  The two acl_users are completely independants. They can even be of different kinds.
  For example, a Zope UserFolder for Groups management and an LDAPUserFolder for Users management.

  Inside the "Users" acl_users, groups are seen as ROLES (that's what we call "groles") so that 
  roles can be assigned to users using the same storage as regular users. Groups are prefixed
  by "group_" so that they could be easily recognized within roles.

  Then, on the top GroupUserFolder, groups and roles both are seen as users, and users have their
  normal behaviour (ie. "groles" are not shown), except that users affected to one or several groups
  have their roles extended with the roles affected to the groups they belong to.


  Just for information : one user can belong to zero, one or more groups.
  One group can have zero, one or more users affected.


GROUPS BEHAVIOUR

  
  ...will be documented soon...


GRUF AND PLONE

  See the dedicated README-Plone file.


GRUF AND SimpleUserFolder

  You might think there is a bug using GRUF with SimpleUserFolder (but there's not): if you create
  a SimpleUserFolder within a GRUF a try to see it from the ZMI, you will get an InfiniteRecursionError.

  That's because SimpleUserFolder tries to fetch a getUserNames() method and finds GRUF's one, which 
  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's one, 
  which tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's one, 
  which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's 
  one, which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds 
  GRUF's one, which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and 
  finds GRUF's one, which  tries to call SimpleUserFolder's one which tries (see what I mean ?)

  To avoid this, just create a getUserNames() object (according to SimpleUserFolder specification) in the folder
  where you put your SimpleUserFolder in (ie. one of 'Users' or 'Groups' folders).

  GRUF also implies that the SimpleUserFolder methods you create are defined in the 'Users' or 'Groups' folder.
  If you define them above in the ZODB hierarchy, they will never be acquired and GRUF ones will be catched
  instead, causing infinite recursions.

BUGS

  There is a bug using GRUF with Zope 2.5 and Plone 1.0Beta3 : when trying to join the plone site
  as a new user, there is a Zope error "Unable to unpickle object"... I don't know how to fix that now.
  With Zope 2.6 there is no such bug.


