PloneFormMailer 

 PloneFormMailer is a Plone product which make it easy to create forms through 
 the web (ttw) and send them formatted to one or more fixed recipients. After 
 successful sending a form, a very easy customizeable response-page will be 
 displayed.

 It combines the power of Formulator and CMFFormController glued together in an 
 Archetypes product, which was initially created by ArchGenXML.

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

  PloneFormMailer resides in the 'collective'
  http://sourceforge.net/projects/collective

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
  And also thanks to all contributors of all minor changes.

 Contribution:

  If you like to help out in writing code and/or documentation, just start 
  and cvs commit. Ok, bigger changes would be nice to discuss ;-)

 Known Bugs:

  * pressing reload on sent-page resent the message - bad behaviour.  

  * DateTime Fields are not rendered in E-Mail. Someone needs to fix the 
    default mailtemplate.

 Todo:

  For Version 0.2

  * encryption: import a public key or get it from keyserver, 
    if not in current keyring

  * fix DateTime Fields

  * review with using SecureMailHost 

  * redirect to 'sent-page' after mail is sent

  * testing, bugfixing
  
  For Version 0.3 and future

  * seperate Formulator-Integration and Mailer in two products

  * integrate Formulator in Plone-UI


