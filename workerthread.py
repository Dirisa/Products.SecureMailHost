"""Worker thread to run code async in a loop
"""

import threading

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
        self._event = threading.Event() # event handler to time the loop
        self._running = False           # thread is stop until calling start
        self._wait = float(wait)
        assert(target is None or callable(target))
        self._target = target
        self._args = args
        self._kwargs = kwargs
        
    def start(self):
        """Start the thread
        """
        self._running = True
        self._event.clear() # enable event timer
        threading.Thread.start(self)
        
    def run(self):
        """Infinitive loop
        """
        while True:
            if not self._running:
                return
            self.main()
            self._event.wait(self._wait)

    def main(self):
        """Worker method
        """
        if self._target:
            self._target(*self._args, **self._kwargs)
        else:
            print 'Does nothing'

    def stop(self):
        """Stop the thread
        
        Required for unit tests
        """
        if not self._running:
            self._running = False
            self._event.set()

def initialize():
    worker = WorkerThread(name='Worker', wait=10.0)
    worker.setDaemon(True)
    worker.start()
