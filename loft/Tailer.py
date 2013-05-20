import Queue
import threading
import time
import logging
import os.path


class FileTailer(threading.Thread):
    """
    Initializes FileTailer and starts tailing log file
    """
    def __init__(self, queue, logFile, stopEvent=threading.Event()):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.queue = queue
        self.logFile = logFile
        self.stopEvent = stopEvent

    def run(self):
        # as loft may start prior to what is being monitored,
        # loft will wait eternally for it to start
        while os.path.isfile(self.logFile) is not True:
            if not self.stopEvent.is_set():
                self.logger.error(self.logFile + ' not yet found.')
                print(self.logFile + ' not yet found.')
                time.sleep(5)
        try:
            with open(self.logFile, 'r') as f:
                self.logger.info('Opening ' + self.logFile)
                f.seek(0)
                while not self.stopEvent.is_set():
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    self.queue.put(line)
        except:
            self.logger.error(self.logFile + ' cannot be opened.')


class getFile(threading.Thread):
    def __init__(self, queue, stopEvent=threading.Event()):
        threading.Thread.__init__(self)
        self.queue = queue
        self.stopEvent = stopEvent

    def run(self):
        while not self.stopEvent.is_set():
            line = self.queue.get()
            print (line)



def main():

    raw_queue = Queue.Queue()
    m1 = FileTailer(raw_queue, r'../test/messagesTail')
    m1.daemon = True
    m1.start()
    print (m1)

    m2 = FileTailer(raw_queue, r'../test/messages-20130403')
    m2.daemon = True
    m2.start()
    print (m2)

    raw_queue.join()

if __name__ == "__main__":
    main()