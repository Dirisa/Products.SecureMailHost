

This file will be used to communicate with other developers
via [collective checkins]

Alarms: informations about broken code 
  - please add an alarm and an email addrress to notify.
  
  
======================================================================
Alarm 1: mirto busico - m.busico@ieee.org
The file helpcenter_view.pt results broken for the i18n translation
CVS head downloaded 4 Feb 2005
Lines 120 -146
                       <a tal:attributes="href help_type/getURL;
                                           title help_type/Description|nothing;">
                        Latest <span tal:replace="help_type/Title">[type]</span>
                        </a>
                        </h6>
[snip]                        
                            <div class="portletContent odd">
                                <a class="portletMore"
                                   tal:attributes="href help_type/getURL" 
                                   tal:content="structure string: All ${help_type/Title}&#8230;"
                                   >All FAQs</a>
                            </div>

The correction used to translate "Latest" and "All" was deleted
With this code you obtain, in italian:
"Latest Domande frequenti" instead of "Le ultime Domande Frequenti"
and
"All Domane Frequenti" instead of "Tutte le Domande Frequenti"

Please, send me a mail when I'll can do again the correction
 
======================================================================