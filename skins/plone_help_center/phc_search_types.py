## Script (Python) "phc_search_types"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Determine which portal_types to search

request = context.REQUEST

choice = request.form.get("phc_selection")

if choice=="faq":
	result=['HelpCenterFAQ','HelpCenterFAQFolder']
elif choice=="howto":
	result=["HelpCenterHowTo","HelpCenterHowtoFolder"]
elif choice=="tutorial":
	result=["HelpCenterTutorial","HelpCenterTutorialFolder","HelpCenterTutorialPage"]

else:
	# choice must have been "all documentation"
	result=['HelpCenterErrorReference','HelpCenterFAQ','HelpCenterGlossary',
	'HelpCenterHowto','HelpCenterLink','HelpCenterTutorial','HelpCenterTutorialPage',
	'HelpCenterLink']


return result	
