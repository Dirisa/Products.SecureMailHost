##############################################################################
#
# Copyright (c) 2004 Christian Heimes and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
"""
try:
    True
except NameError:
    True=1
    False=0

import os
import smtplib
from Globals import INSTANCE_HOME

## email settings
# X-Mailer header of email
X_MAILER = 'Zope/SecureMailHost'

# unallowed headers
BAD_HEADERS = ()

## async mailer settings
# use async mail thread?
# WARNING: Make shure that your queue is empty before disabling the async mailer
USE_ASNYC_MAILER=False
USE_ASNYC_MAILER=True

# sleep time for the main thread loop
WAIT_TIME = 30

# max fatal errors before an email is discarded
MAX_ERRORS = 5

# non fatal (aka temporary) errors
TEMP_ERRORS = (smtplib.SMTPConnectError, )

# path and name of the anydb database which holds a backup of the mail queue
DB_FILE = os.path.join(INSTANCE_HOME, 'var', 'securemail_queue.db')
