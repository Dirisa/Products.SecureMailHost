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
elif choice=="link":
    result=["HelpCenterLink","HelpCenterLinkFolder"]
elif choice=="error":
    result=["HelpCenterErrorReference","HelpCenterErrorReferenceFolder"]
elif choice=="glossary":
    result=["HelpCenterDefinition","HelpCenterGlossary"]
elif choice=="manual":
    result=["HelpCenterReferenceManual","HelpCenterReferenceManualFolder",
            "HelpCenterReferenceManualSection","HelpCenterReferenceManualPage"]
elif choice=="video":
    result=["HelpCenterInstructionalVideo","HelpCenterInstructionalVideoFolder"]
    

else:
	# choice must have been "all documentation"
	result=['HelpCenterFAQ',
            'HelpCenterHowto',
            'HelpCenterTutorial',
            'HelpCenterTutorialPage',
            'HelpCenterLink',
            'HelpCenterErrorReference',
            'HelpCenterDefinition',
            'HelpCenterReferenceManual',
            'HelpCenterReferenceManualSection',
            'HelpCenterReferenceManualPage',
            'HelpCenterInstructionalVideo']

return result	
