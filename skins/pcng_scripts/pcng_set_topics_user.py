##parameters=topic,users
# Save Topic-user mapping

T = context.getTopics().setUsers(topic, users)
context.REQUEST.RESPONSE.redirect('pcng_topics_user?portal_status_message=%s' % context.Translate('topic_user_mapping_saved', 'Topic-User preferences saved'))

