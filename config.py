#------------------------------------------------------------------------------
# Name:         config.py
# Purpose:      some defaults and settings for PloneFormMailer
#
# Author:       Jens Klein <jens.klein@jensquadrat.de>
#
# RCS-ID:       $Id: config.py,v 1.2 2004/08/12 16:52:40 yenzenz Exp $
# Copyright:    (c) 2004 by jens quadrat, Klein & Partner KEG, Austria
# Licence:      GNU General Public Licence (GPL) Version 2 or later
#------------------------------------------------------------------------------


default_mailtemplate_subject = \
"""string:PloneFormMailer"""

default_mailtemplate_body = \
"""<tal:block i18n:domain="PloneFormMailer" 
           tal:define="form here/form;
                       groups form/get_groups;">
<html>
<body>
<pre tal:content="here/getBody_pre" />
<pre tal:content="options/prepend" />

<tal:block tal:repeat="group groups">
  <pre tal:condition="python:group!='Default'" tal:content="group" />
  <tal:block tal:repeat="field python:form.get_fields_in_group(group)">
    <tal:block tal:condition="python:here.REQUEST.get('field_%s' % field.id, '')">
      <pre tal:content="python:'['+field.title()+']'" />
      <pre tal:content="python:here.REQUEST.get('field_%s' % field.id, '')" /><br />
    </tal:block>
    <tal:block tal:condition="field/sub_form | nothing">
     <pre tal:content="python:'['+field.title()+']'" />
      <tal:block tal:repeat="sub_field python:sub_form.get_fields()">
        <pre>subform renderer not implemented'</pre>
      </tal:block>
    </tal:block>
  </tal:block>
</tal:block>

<pre tal:content="options/append" />
<pre tal:content="here/getBody_post" />
<pre tal:content="here/getFooter" />
</body>
</html>
</tal:block>"""

