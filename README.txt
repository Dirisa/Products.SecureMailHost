SecureMailHost
==============

SecureMailHost is a reimplementation of the standard MailHost with some security
and usability enhancements:

  * ESMTP login on the mail server based on the MailHost from 
    http://www.zope.org/Members/bowerymarc

  * Start TLS (ssl) connection if possible

  * Usage of Python 2.3's email package which has multiple benefits like easy to
    generate multi part messages including fance HTML emails and with images.

  * Releases are shipped with a compatibility version of email for older pythons.

  * A new secureSend() method that seperates headers like mail to, mail from
    from the body text. You don't need to mingle body text and headers any more.

  * Email address validation based on the code form PloneTool for mail from,
    mail to, carbon copy and blin carbon copy to prevent spam attacks. 
    (Only for secureSend()!)

  * Message-Id and X-Mailer header generation to lower the spam hit points of
    Spam Assassin.

  * An async mailer thread is using a new thread to send emails including a
    seperate Mail class and a MailQueue with auto-backup on the file system.
    The seperate mail thread will prevent Zope from blocking while connecting
    to the external SMTP server.
    (Disabled by default)

Author:
    Christian Heimes <heimes@faho.rwth-aachen.de>

License:
    ZPL 2.1

Downloads and bug collector:
    http://sf.net/projects/collective/
