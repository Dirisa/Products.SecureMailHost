PloneClipboard
==============


Dependencies
------------
PloneClipboard requires
    * Archetypes from release-1_3-branch,
    * Plone >= 2.0,
    * ReferenceFolder (not released).

A version of ReferenceFolder may be temporarily downloaded from this URL:
http://algorhythmus.con-fuse.org/tmp/ReferenceFolder.tar.gz .


User Model
----------
PloneClipboard creates for each authenticated user a set of clipboards
(aka ReferenceBags), which behave like ordinary ordered folders. Clipboards
are stored in the *.clipboards* subdirectory of the member's folder.

Now everytime you copy a set of objects into the copy buffer, you will have the
option to put the contents of the buffer into one of your clipboards.

In addition to copying objects from folder listings, PloneClipboard allows you
to copy objects that are the result of a search.

Using a specialised widget, you can then use the contents of your clipboards
to build references between objects.


Implementation
--------------
Note that only objects that are of type ``IReferencable`` can be put into a
clipboard. This means that Plone 2.0 content objects won't work while any
Archetypes objects (such as the ATCT_ replacement types) will.

.. _ATCT: http://cvs.sourceforge.net/viewcvs.py/collective/ATContentTypes/

The reference widget that comes with PloneClipboard works on top of Archetypes'
ReferenceField. You use it like so::

    from Products.Archetypes.public import *
    from Products.PloneClipboard import ReferenceClipboardWidget, \
                                        ReferenceClipboardValidator
    
    reffield = ReferenceField('authors',
                              widget=ReferenceClipboardWidget,
                              validators=(ReferenceClipboardValidator,))
    schema = BaseSchema + Schema(reffield)

PloneClipboard comes with its own version of ``search.pt`` that's compatible
with Plone 2.0.


Feedback
--------
The author's e-mail address is daniel.nouri@con-fuse.org . I'm also often in
*#plone* on *freenode.net* as **Hellfried**.

PloneClipboard is Copyright (C) 2004 Material Thought, Inc (dba iTec Solutions)
and Contributors <russf@topia.com>. See COPYING.