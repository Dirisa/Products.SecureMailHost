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
"""Worker thread to run code async in a loop
"""
try:
    True
except NameError:
    True=1
    False=0

import threading


class ReadWriteLock:
    """A lock object that allows many simultaneous "read-locks", but
    only one "write-lock".
    
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66426
    """
    
    def __init__(self):
        self.__read_ready = threading.Condition(threading.Lock())
        self.__readers = 0

    def acquire_read(self):
        """Acquire a read-lock. Blocks only if some thread has
        acquired write-lock."""
        self.__read_ready.acquire()
        try:
            self.__readers += 1
        finally:
            self.__read_ready.release()

    def release_read(self):
        """Release a read-lock."""
        self.__read_ready.acquire()
        try:
            self.__readers -= 1
            if not self.__readers:
                self.__read_ready.notifyAll()
        finally:
            self.__read_ready.release()

    def acquire_write(self):
        """Acquire a write lock. Blocks until there are no
        acquired read- or write-locks."""
        self.__read_ready.acquire()
        while self.__readers > 0:
            self.__read_ready.wait()

    def release_write(self):
        """Release a write-lock."""
        self.__read_ready.release()


class WorkerThread(threading.Thread):
    """Common Worker Thread
    
    worker = WorkerThread(name='name', wait=float(10))
    worker.setDaemon(True)
    worker.start()
    # calling main() method every 10 seconds until stopped
    worker.stop() # stopped
    worker.start() # started again
    
    name     - name of the thread
    wait     - timer for the main loop
    target   - a callable or None
    *args    - optional args for the target
    **kwargs - optinal keyword arguments for the target
    
    Do NOT overwrite the run() method. Overwrite the main() method or apply
    a target.
    """
    
    def __init__(self, name='WorkerThread', wait=10.0, target=None, *args, **kwargs):
        threading.Thread.__init__(self, name=name)
        self.setDaemon(True)
        self.__event = threading.Event() # event handler to time the loop
        self.__running = False           # running status
        self.__wait = float(wait)        # sleep time

        assert(target is None or callable(target))
        self.__target = target
        self.__args = args
        self.__kwargs = kwargs
        
    def start(self):
        """Start the thread
        """
        self.__event.clear() # enable event timer
        self.__running = True
        threading.Thread.start(self)
        
    def run(self):
        """Infinitive loop
        """
        try:
            while self.__running:
                self.main()
                self.__event.wait(self.__wait)
        except SystemExit:
            self.stop()
        except TypeError, msg:
            # XXX hack to prevent an ugly message
            # Remove it after upgrading to Python 2.4
            # http://marc.free.net.ph/message/20040517.043622.15770319.html
            if str(msg) == "'NoneType' object is not callable":
                pass
            else:
                raise

    def main(self):
        """Worker method
        """
        if self.__target:
            self.__target(*self.__args, **self.__kwargs)
        else:
            print 'Does nothing'

    def stop(self):
        """Stop the thread
        
        Required for unit tests
        """
        self.__running = False
        self.__event.set()

    def kick(self):
        """Kicks the thread to do it's work
        
        This will force to run the main loop by shortly disabling the event
        timer unless it is already running.
        """
        # copy old state
        oldState = bool(self.__running)
        self.__runing = True
        self.__event.set()
        # RUN Forest run!
        self.__event.clear() # reenable event timer
        self.__running = oldState


def initialize():
    worker = WorkerThread(name='Worker', wait=10.0)
    worker.start()

__all__ = ('WorkerThread', 'ReadWritLock', 'initialize', )
