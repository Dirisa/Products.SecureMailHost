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
"""Compatibility package for python < 2.3.3

Installs email package from 2.3.4
"""
import sys
import os
from zLOG import LOG, INFO, PROBLEM
from Globals import SOFTWARE_HOME

MINIMAL_PYTHON_VERSION = (2, 3, 3) # tuple of ints
MINIMAL_EMAIL_VERSION = '2.5.4' # string
EMAIL_PACKAGE = '2.5.5' # string

basepath = os.path.dirname(os.path.abspath(__file__))
email_path = '%s/email-%s' % (basepath, EMAIL_PACKAGE)

if sys.version_info < MINIMAL_PYTHON_VERSION:
    if os.path.isdir(email_path):
        # insert email package into python's search path
        # index 3: after zope's pathes but before python
        sys.path.insert(3, email_path)
        
        LOG('SecureMailHost:', INFO, 'Added email package %s to python path ' \
            'because your python version has no package or an older package.' \
             % EMAIL_PACKAGE)
    else:
        LOG('SecureMailHost:', PROBLEM, 'Can\'t install email package from %s ' \
            'but it\'s required for SecureMailHost!' % email_path)
        raise RuntimeError('No valid email package found!')

import email
if email.__version__ < MINIMAL_EMAIL_VERSION:
    raise RuntimeError('Your version of the email package is too old for ' \
        'SecureMailHost. Your version: %s, required: %s. Please copy the '\
        '\'email\' directory from %s/ to %s/.' \
        % (email.__version__, MINIMAL_EMAIL_VERSION, email_path,SOFTWARE_HOME))
