## Script (Python) "breadcrumbs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=used to make the breadcrumbs in the pathbar
##
if obj is None:
    obj=context

portal=context.portal_url.getPortalObject()
parents = []
p = obj
while p != portal:
    parents.append(p)
    p = p.getParentNode()
parents.reverse()

# some variables
published = context.REQUEST.get('PUBLISHED', None)
published_id = None
checkPermission=context.portal_membership.checkPermission
dont_show = ['talkback',] # objects we wont show

if published is not None and hasattr(published, 'getId'):
    published_id = published.getId()

currentlyViewingFolderContents = (published_id in ['folder_contents', 'folderContents'])
path_seq = []

o = portal
# add breadcrumbs for directories between the root and the published object
for o in parents:
#for id in relative_ids:    
    # this is much faster than restrictedTraverse and makes some sense,
    # if the user can't access the contents information, getattr() will fail
    # and hiding the breadcrumb because they dont have access? urk
    # o = getattr(o, id)
    if hasattr(o, 'getId') and callable(o.getId):
        id = o.getId()
    else:
        id = getattr(o, 'id', '')
    if id in dont_show: # I'm sorry ;(
        # talkbacks would clutter our precious breadcrumbs
        continue

    if o.isPrincipiaFolderish and \
      currentlyViewingFolderContents and \
      checkPermission('List folder contents', o):
        path_seq.append( ( o.title_or_id(), o.absolute_url()+'/folder_contents') )
    else:
        # we assume in search results everything has a view
        # and if every object is derived from PortalObject, it
        # must have a method called view, so I think its pretty
        # safe to make this assumption, and adds a speed increase
        if str(id) != 'index_html':
            path_seq.append( ( o.title_or_id(), o.absolute_url()+'/view' ) )

# if the published object was not added to breadcrumbs above and
#    it is not a view template, add a breadcrumb for it

# under some circunstances (read ZWiki :P) 'published' may
# be a method. A method doesnt have title_or_id, and even if it had
# it would not be accessible from here.

if published != o and not \
    currentlyViewingFolderContents and \
    published_id not in  ('view', 'index_html') and \
    hasattr(published, 'title_or_id'):
      url = published.absolute_url() + '/view'
      path_seq.append( (published.title_or_id(), url) )

return path_seq
