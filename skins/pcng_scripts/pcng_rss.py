# Basic script to provide RSS support based on ZCatalog queries

# Search the issues to be RSS-ified
result = context.pcng_catalog(last_action = {'query' : DateTime()-14, 'range': 'min'},) 

# Render XML
xml = context.pcng_rss_template(result=result)

# Send everything back
context.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
context.REQUEST.RESPONSE.setHeader('content-length', len(xml))
context.REQUEST.RESPONSE.write(xml)
