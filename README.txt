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

 * i18n support with LinguaPlone (optional)

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

 Support

  There isn't enough traffic for a own mailing-list. So feel free to post to
  the "plone-users list":http://plone.org/documentation/lists/

 Known Bugs, Bug-Tracker

  Search the "bugtracker":http://sourceforge.net/tracker/?group_id=55262&atid=476390 
  at sourceforge.net in the project collective. Report bugs and if possible drop 
  bugfixes.

 Todo:
  
  Version 0.3 

  * review with using SecureMailHost 

  * better MailTemplate

  * encryption: import a public key or get it from keyserver, 
    if not in current keyring

  * cover form translation by some better method.

  Future ideas ...

  * seperate Formulator-Integration and Mailer in two products

  * integrate Formulator in Plone-UI


