##parameters=topic

# Add a new topic

context.getTopics().addTopic(topic)
msg =context.Translate('topic_added', 'Topic added')
context.REQUEST.RESPONSE.redirect('pcng_topics_user?portal_status_message=%s' % msg)
