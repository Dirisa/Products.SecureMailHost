##parameters=topic,users
# Save Topic-user mapping

context.set_topic_users(topic, users)
context.REQUEST.RESPONSE.redirect('pcng_topics_user?portal_status_message=%s' % context.Translate('topic_user_mapping_saved', 'Topic-User preferences saved'))

