# translate path

url = context.absolute_url(1)
url1 = context.REQUEST['URL1']
pos = url1.find(url)

s = url1[pos + len(url):]

if hasattr(context, 'folder_address_display_style'):
	addressDisplayStyle = getattr(context, 'folder_address_display_style')
else:
	addressDisplayStyle = 'PLFNG_Base_Relative'

if addressDisplayStyle == 'PLFNG_Base_Relative':
	s = url1[pos + len(url):] 

#s = s.replace('plfng_view','')
#s = s.replace('folder_contents','')
s = s + '/'
return s
