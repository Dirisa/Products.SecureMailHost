"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: util.py,v 1.2 2004/09/11 12:19:05 ajung Exp $
"""

import os
import logging
from ConfigParser import ConfigParser

CFG_FILE = '.smtp2pcng.cfg'
MAX_LENGTH = 32768

LOG = None

def getLogger():
    """ return logger instance """

    global LOG

    if not LOG:
        LOG = logging.getLogger('pcng')
        hdlr = logging.FileHandler('smtp2pcng.log')
        hdlr1 = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(process)s %(message)s')
        hdlr.setFormatter(formatter)
        hdlr1.setFormatter(formatter)
        LOG.addHandler(hdlr)
        LOG.addHandler(hdlr1)
        LOG.setLevel(logging.DEBUG)

    return LOG

def getConfiguration():
    """ return configuration object """

    LOG = getLogger()

    CFG_LOCATIONS = (os.getcwd(), os.path.expanduser('~'))
    config = ConfigParser()                               
    files = []
    for loc in CFG_LOCATIONS:
        cfg_name = os.path.join(loc, CFG_FILE)
        if not os.path.exists(cfg_name):
            LOG.warn('No configuration file %s found' % cfg_name)
        else:
            LOG.debug('Reading configuration file %s ' % cfg_name)
            files.append(cfg_name)

    if not files:
        LOG.warn('No suitables configuration files found')
    else:
        config.read(files)

    return config

def update_options(options, config):

    """ update the options objects from informations 
        in the configuration file 
    """

    if options.configuration:

        section = options.configuration
        if not config.has_section(section):
            raise ValueError("Section '%s' not found in configuration file" % section)
        for op in ('url', 'username', 'password'):
            if not config.has_option(section, op):
                raise ValueError("Section '%s' has no option '%s'" % (section, op))

        options.url = config.get(section, 'url')
        options.username = config.get(section, 'username')
        options.password = config.get(section, 'password')
        if config.has_section('default'):
            if config.has_option('default', 'maxlength'):
                options.max_length = int(config.get('default', 'maxlength'))     
            else:
                options.max_length = MAX_LENGTH

