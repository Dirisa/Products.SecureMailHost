##parameters=timestamp

# Delete the comment of a transcript event

from AccessControl import getSecurityManager

context.getTranscript().deleteEntry(timestamp)

context.getTranscript().addComment(context.Translate('transcript_entry_deleted', 
           'Transcript entry ($date) deleted by $user', 
           hidden=1,
           date=context.toLocalizedTime(DateTime(float(timestamp)), long_format=1),
           user=getSecurityManager().getUser().getUserName(), as_unicode=1))
                                                                                                               
context.REQUEST.RESPONSE.redirect(context.absolute_url())
