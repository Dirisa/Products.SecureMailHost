#------------------------------------------------------------------------------
# Name:         config.py
# Purpose:      some defaults and settings for PloneFormMailer
#
# Author:       Jens Klein <jens.klein@jensquadrat.de>
#
# RCS-ID:       $Id: config.py,v 1.6 2004/10/20 20:17:06 dreamcatcher Exp $
# Copyright:    (c) 2004 by jens quadrat, Klein & Partner KEG, Austria
# Licence:      GNU General Public Licence (GPL) Version 2 or later
#------------------------------------------------------------------------------

GLOBALS = globals()
ADD_CONTENT_PERMISSION = 'Add PloneFormMailer content'
PROJECTNAME = 'PloneFormMailer'

default_mailtemplate_subject = \
"""string:PloneFormMailer"""

default_mailtemplate_body = \
"""<tal:block i18n:domain="pfm"
           tal:define="form here/form;
                       groups form/get_groups;">
<html>
<body>
<p tal:condition="here/getBody_pre" tal:content="here/getBody_pre" />
<p tal:condition="options/prepend" tal:content="options/prepend" />

<tal:block tal:repeat="group groups">
  <h1 tal:condition="python:group!='Default'" tal:content="group" />
  <dl>
    <tal:block tal:repeat="field python:form.get_fields_in_group(group)">
        <dt i18n:translate="" tal:content="python:field.title()" />
        <dd tal:define="lines python:str(field.validate(here.REQUEST)).splitlines()">
          <tal:block tal:repeat="line lines">
            <span tal:content="line" /><br />
          </tal:block>
        </dd>
    </tal:block>
  </dl>
</tal:block>

<p tal:condition="options/append" tal:content="options/append" />
<p tal:condition="here/getBody_post" tal:content="here/getBody_post" />
<pre tal:content="here/getFooter" />
</body>
</html>
</tal:block>"""

# LinguaPlone addon?
try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    HAS_LINGUA_PLONE = False
else:
    HAS_LINGUA_PLONE = True
