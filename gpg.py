#------------------------------------------------------------------------------
# Name:         gpg.py
# Purpose:      Provides a GPGSubprocess class that can be used to encrypt,
#               decrypt, sign, and verify GPG messages.  It runs GPG in batch
#               mode, which causes it to output lines prefixed with '[GNUPG:]'
#               that contain well-structured information about the results.
#
# Author:       Jens Klein <jens.klein@jensquadrat.de>
# copied:       from python-gpg project (unfinished)
#
# Created:      Sun Jan 25 22:09:22 2004
# RCS-ID:       $Id: gpg.py,v 1.2 2004/10/20 20:17:06 dreamcatcher Exp $
# Copyright:    (c) 2004 by jens quadrat GbR, Germany
# Licence:      GNU General Public Licence (GPL) Version 2 or later
#------------------------------------------------------------------------------

"""GPG module

Provides a GPGSubprocess class that can be used to encrypt, decrypt,
sign, and verify GPG messages.  It runs GPG in batch mode, which causes it
to output lines prefixed with '[GNUPG:]' that contain well-structured
information about the results.
"""

__revision__ = '$Id: gpg.py,v 1.2 2004/10/20 20:17:06 dreamcatcher Exp $'

import os, string, sys, tempfile
import cStringIO, popen2

class gpg_subprocess:

    # Default path used for searching for the GPG binary, when the
    # PATH environment variable isn't set.
    DEFAULT_PATH = ['/bin', '/usr/bin', '/usr/local/bin']

    def __init__(self, gpg_binary = None):
        """Initialize an object instance.  Options are:

        gpg_binary -- full pathname for GPG binary.  If not supplied,
        the current value of PATH will be searched, falling back to the
        DEFAULT_PATH class variable if PATH isn't available.
        """
        # If needed, look for the gpg binary along the path
        if gpg_binary is None:
            gpg_binary = self._findbinary('gpg')
        self.gpg_binary = gpg_binary
        if gpg_binary is None:
            # error
            pass

    def _findbinary(self,binname):
        import os
        if os.environ.has_key('PATH'):
            path = os.environ['PATH']
            path = string.split(path, os.pathsep)
        else:
            path = self.DEFAULT_PATH
        for dir in path:
            fullname = os.path.join(dir, binname)
            if os.path.exists( fullname ):
                return fullname
        return None

    def _open_subprocess(self, *args):
        # Internal method: open a pipe to a GPG subprocess and return
        # the file objects for communicating with it.
        cmd = self.gpg_binary + ' --yes --status-fd 2 ' + string.join(args)
        child_stdout, child_stdin, child_stderr = popen2.popen3(cmd)
        return child_stdout, child_stdin, child_stderr


    def encrypt_file(self, input, output, recipient_key_id):
        "Encrypt the message read from the file-like object 'input'"
        child_stdout, child_stdin, child_stderr = \
            self._open_subprocess('--encrypt',
                '-r '+ recipient_key_id,
                input.name,
                output.name)
        return child_stdout, child_stdin, child_stderr

    def encrypt(self, data, recipient_key_id):
        "Encrypt the message contained in the string 'data'"

        # get communication objects
        child_stdout, child_stdin, child_stderr = \
            self._open_subprocess('--encrypt',
                '-a',
                '-r '+ recipient_key_id)

        # feed data
        child_stdin.write(data)
        child_stdin.close()

        # get response
        datagpg = child_stdout.read()

        return datagpg

    def import_key(self,keydata):
        "Import a key"
        child_stdout, child_stdin, child_stderr = \
            self._open_subprocess('--import')

        # feed data
        child_stdin.write(keydata)
        child_stdin.close()

        # get response
        output = child_stdout.read()
        output = child_stdout.read()


if __name__ == '__main__':

    obj = gpg_subprocess()
    #data =
    data = obj.encrypt('BLABLA','1A7D064A')
    print data
