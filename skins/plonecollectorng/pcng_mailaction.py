##parameters=body,subject

staff = context.getTrackerUsers(staff_only=1)
emails = [u.get('email') for u in staff]
dest_emails = [e for e in emails if e]
MH = getattr(context, 'MailHost') 
try:
    MH.send(body, dest_emails, context.collector_email, subject) 
    msg = context.Translate('message_sent', 'Message has been sent')
except:
    msg = context.Translate('error_message_sent', 'Error sending the message')
context.REQUEST.RESPONSE.redirect('pcng_maintenance?portal_status_message=%s' % msg)
