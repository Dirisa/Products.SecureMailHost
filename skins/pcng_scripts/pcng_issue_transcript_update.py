##parameters=comment,timestamp

# Update the comment of a transcript event

from AccessControl import getSecurityManager

context.getTranscript().modifyEntry(timestamp, comment=comment)

context.getTranscript().addComment(context.Translate('transcript_edited_by', 
           'Transcript entry ($date) edited by $user', 
           date=context.toLocalizedTime(DateTime(float(timestamp)), long_format=1),
           user=getSecurityManager().getUser().getUserName(), as_unicode=1))

                                                                                                               
context.REQUEST.RESPONSE.redirect(context.absolute_url())


