##parameters=query

# Perform a search stored as QUERY_STRING in the pcng_saved_searches
# property of a member

context.REQUEST.RESPONSE.redirect('pcng_view?%s' % query)
