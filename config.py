"""
"""
import os
import smtplib
from Globals import INSTANCE_HOME

X_MAILER = 'Zope/SecureMailHost'
BAD_HEADERS = ()

WAIT_TIME = 30
MAX_ERRORS = 5
TEMP_ERRORS = (smtplib.SMTPConnectError, )
# XXX MAX_UID_LOOP = 10000
DB_FILE = os.path.join(INSTANCE_HOME, 'var', 'securemail_queue.db')
