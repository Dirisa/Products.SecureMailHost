##parameters=parameters

# Script to create an new issue. 'parameters' is a Zope record
# object that is used to update the attributes of the issue.
#
# For TTW code this should look like:
# 
# <form action="pcng_add_issue">
# <input type="text" name="parameters.title:record:string"....
# <input type="text" name="parameters.description:record:string"....
# .....
# </form>
#

id = context.add_issue()                # create a new issue skeleton
context[id].setParameters(parameters)   # update parameters

context.REQUEST.RESPONSE.redirect(context.absolute_url() + "/" + id)
