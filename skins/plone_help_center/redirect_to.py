## Script (Python) "redirect_to"
##title=Simple Redirection
##parameters=dest

return context.REQUEST.RESPONSE.redirect('%s/%s' % (context.absolute_url(),
                                                    dest))
