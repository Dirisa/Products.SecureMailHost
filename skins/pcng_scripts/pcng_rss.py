
# Basic script to provide RSS support based on ZCatalog queries.
# If no keyword parameters (search query) is specified then we return
# all active issues over the last two weeks.

if not context.REQUEST.get('QUERY_STRING'):
    context.REQUEST.set('last_action',  {'query' : DateTime()-14, 'range': 'min'}) 

# Search the issues to be RSS-ified
result = context.pcng_catalog(context.REQUEST)

# Render XML
xml = context.pcng_rss_template(result=result)

# Send everything back
context.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
context.REQUEST.RESPONSE.setHeader('content-length', len(xml))
context.REQUEST.RESPONSE.write(xml)
