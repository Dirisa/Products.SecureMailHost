# translate path

url = context.absolute_url(1)
url0 = context.REQUEST['URL0']
pos = url0.find(url)
	
if context.diplayFullPortalPath():
	s = url
else:
	s = url0[pos + len(url):]
s = s.replace('plfng_view','')

return s
