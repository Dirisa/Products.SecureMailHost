
# Save Topic-user mapping

context.set_topics_user(context.REQUEST['topics'])
context.REQUEST.RESPONSE.redirect('pcng_topics_user?portal_status_message=%s' % context.translate('topic_user_mapping_saved', 'Topic-User preferences saved'))

