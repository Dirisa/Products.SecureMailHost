PloneFormMailer 

 PloneFormMailer is a Plone product which make it easy to create forms through 
 the web (ttw) and send them formatted to one or more fixed recipients. After 
 successful sending a form, a very easy customizeable response-page will be 
 displayed.

 It combines the power of Formulator and CMFFormController glued together in an 
 Archetypes product, which was created by ArchGenXML.

 PloneFormMailer is designed to be customized very easy.

Features:

 * send web-forms via e-mail, like contact forms, order forms, etc.

 * form creation via formulator; fully customizeable

 * customizeable mail header and body with PageTemplates

 * TALES support for recipients name, e-mail, cc, bcc

 * add header and footer (txt, stx, html, ...) to form

 * optional use of own controller page template

 * customizeable response page (displayed after succeccful send)

 * optional response redirect with TALES support

 * encrypt message using a gpg

 Download

  PloneFormMailer resides in BlueDynamics public CVS. 
  http://cvs.bluedynamics.org/viewcvs/PloneFormMailer

 Author

  Jens Klein <jens.klein@jensquadrat.de> jens quadrat GbR, Germany/Austria

 Licence

  This product is under GNU General Public Licence Version 2 or later

 Credits

  Thanks to Daniel Nouri, who did basic case-studies with Uniformed and added 
  TALES support. 
  Thanks to the unknown author of the howto at plone.org "Integrating 
  CMFFormController with Formulator":http://plone.org/documentation/howto/IntegratingCMFFormControllerWithFormulator
  and also to the authors of CMFFormController and Formulator.

 Known Bugs:

  * pressing reload on sent-page resent the message - bad behaviour.  

  * DateTime Fields are not rendered in E-Mail. Someone needs to fix the 
    default mailtemplate.

 Todo:

  For Version 0.2

  * encryption: import a publickey or get it from keyserver, 
    if not in current keyring

  * testing, bugfixing
  
  For Version 0.3 and future

  * seperate Form-Integration and Mailer in two products

  * generic mail templates, better than zpt-output rendered  with lynx

  * integrate Formulator in Plone-UI


