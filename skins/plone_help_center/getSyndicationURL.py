##parameters=portal_url, my_path, subtypes
return portal_url + '/search_rss?sort_on=modified&sort_order=descending&path=' + my_path + '&' + ('&'.join(['portal_type=%s' % s for s in subtypes ]))
