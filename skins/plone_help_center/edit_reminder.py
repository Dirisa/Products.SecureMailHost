## Script (Python) "redirect_to"
##title=Check edited object and print state-aware message.
##parameters=

wtool = context.portal_workflow

if wtool.getInfoFor(context, 'review_state') == 'in-progress':
    msg = 'Saved.+This+must+be+published+before+it+will+be+visible.+Please+submit+for+review+when+you+are+ready.'
else:
    msg='Your+changes+have+been+saved.'   

return context.REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' % (context.absolute_url(),msg) )
