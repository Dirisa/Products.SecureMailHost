##parameters=topic
# Save Topic-user mapping

T = context.getTopics().deleteTopic(topic)
context.REQUEST.RESPONSE.redirect('pcng_topics_user?portal_status_message=%s' % context.Translate('topic_deleted', 'Topic deleted'))

