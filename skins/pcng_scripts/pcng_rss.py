##parameters=**kw

# Basic script to provide RSS support based on ZCatalog queries.
# If no keyword parameters (search query) is specified then we return
# all active issues over the last two weeks.

if not kw:
    kw = { 'last_action' :  {'query' : DateTime()-14, 'range': 'min'} }

# Search the issues to be RSS-ified
result = context.pcng_catalog(**kw)

# Render XML
xml = context.pcng_rss_template(result=result)

# Send everything back
context.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
context.REQUEST.RESPONSE.setHeader('content-length', len(xml))
context.REQUEST.RESPONSE.write(xml)
