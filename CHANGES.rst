Changelog
=========

2.0 - Unreleased
----------------

- Moved code to https://github.com/collective/Products.SecureMailHost
  [maurits]

- Cleaned up package metadata.
  [hannosch]

- Declare package dependencies and fixed deprecation warnings for use
  of Globals.
  [hannosch]

- Our internal attributes for storing the user and password have changed.
  smtp_userid is now smtp_uid, smtp_pass is smtp_pwd and force_tls has
  been renamned smtp_notls and has an inverted boolean meaning.
  [hannosch]

- Our own mail.py and connection handling is only used for debugging at
  this point.
  [hannosch]

- Removed custom code and reused the base classes functionality at most
  places. This requires the MailHost from Zope 2.11.
  [hannosch]

- Modernized code base and tests.
  [hannosch]

1.1.1 - 2007-08-23
------------------

- First release as a package.
  [hannosch]

1.1 - 2007-07-10
----------------

- Use isinstance to check for types and update code to handle unicode
  email addresses.
  [wichert, optilude, hannosch]

- Made secureSend method handle message text passed in as Unicode. We
  encode it in the given charset now.
  [hannosch]

- Raise an exception if someone tries to send mail without specifying a
  proper SMTP server.
  [wichert]

1.0.5 - 2007-04-22
------------------

- Added a property noTLS to disable SSL. This closes
  http://dev.plone.org/plone/ticket/5342.
  [fenestro, hannosch]

1.0.4 - 2006-05-15
------------------

- For mail servers that refuse the EHLO command we try HELO instead now.
  This closes http://dev.plone.org/plone/ticket/4924.
  [hannosch]

- Undeprecated the send and sendTemplate methods. These are part of the
  generic MailHost API and you are allowed to use them. Note that they do
  not provide all the features of SecureMailHost right now.
  [hannosch]

1.0.3 - 2006-03-19
------------------

- Fixed list->string conversion for recipients list, it's now possible to
  have multiple addressees in to, cc and bcc headers.
  [jenner]

- Fixed handling of non-ascii recipients when a email.Message.Message class
  is handed to secureSend; charset can now be set to the correct encoding
  without raising an error.
  [mj]

1.0.2 - 2005-12-18
------------------

- Fixed tests and update documentation.
  [hannosch]

- Fixed a typo and minor cleanup.
  [sidnei]

- Fixed incorrect error output.
  [rafrombrc]

- Make id optional so SecureMailHost can be setup from CMFSetup.
  [bmh]

1.0.1 - 2005-08-07
------------------

- Fixed problem when smtpserver supports TLS but the local Python
  installation does not support SSL.
  https://trac.plone.org/plone/ticket/4406
  [batlogg] [alecm]

1.0.0 - 2005-07-29
------------------

- Fixed [ 1156733 ] Mails aren't sent to CC and BCC. Addresses in mcc and 
  mbcc weren't added to the recipient list.
  [tiran]

- Made unit tests bin/zopectl test compatible
  [tiran]

- Fixed http://plone.org/collector/4173 and 4201 email adresses are
  RFC 2822 compliant now.
  [hannosch]

1.0-rc1 - 2005-03-02
--------------------

- Fixed [ 1047475 ] message-ids not RFC 2822 compliant. SMH is using
  email.Utils.make_msgid with the fqdn as additional argument.
  [tiran]

- Ripped off the py_compatible module and the threaded feature from SMH.
  py_compatible isn't required any more because Plone needs Zope 2.7.4
  with the new email package and the threaded feature is too experimental.
  [tiran]

1.0-rc1 - 2005-01-27
--------------------

- usernames in email address now encoded by email.Header
  This is especially important for Chinese and other languanges.
  [panjunyong]

0.2-rc3 - 2004-07-19
--------------------

- Changed email package test to import test. This allowes the manual
  installation of the email package into site-packages.

- More compat for python 2.1 in tests/

0.2-rc2 - 2004-07-15
--------------------

- Made SecureMailHost compatible with Python 2.1 (True, False ...)

- Added python compatibility for email package. email 2.5.5 is automagically
  loaded if no email package is found. If an email package < 2.5.4 is found
  SecureMailHost is raising a RuntimeError.

- Shipping releases with email package 2.5.5.

- Added copyright headers and LICENSE.txt file for ZPL 2.1.

0.2-rc1 - 2004-07-09
--------------------

- Better logging at multiple places like awaking thread, sending mail ...

- Mail object supports str() and repr() and has a new method called info()
  which returns some useful informations about the email

- Queue supports len()

- Automagically start threading if ASYNC is used and queue isn't empty.

- Fixed a problem with not showing user and password in the edit template

0.2-beta2 - 2004-05-24
----------------------

- Multiple small fixes to make the old send() method run
  [longsleep, tiran]

0.2-beta1 - 2004-05-24
----------------------

- First beta testing version
  [tiran]

- Implemented all the new stuff like async thread, mailer class, starttls ...
  [tiran]
