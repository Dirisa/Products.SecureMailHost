##parameters=comment,timestamp

# Update the comment of a transcript event

from AccessControl import getSecurityManager

context.getTranscript().modifyEvent(timestamp, unicode(comment, context.getSiteEncoding()))

#context.getTranscript().addComment(context.Translate('transcript_edited_by', 
#           'Transcript entry ($date) edited by $user', 
#           hidden=1,
#           date=context.toLocalizedTime(DateTime(float(timestamp)), long_format=1),
#           user=getSecurityManager().getUser().getUserName(), as_unicode=1))
                                                                                                               
context.REQUEST.RESPONSE.redirect(context.absolute_url())
