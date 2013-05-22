import os,logging, time
import Queue
import Tailer
import Producer
import FilterEngine
from loft.conf.Config import logFileNames

# loft application config
import logging.config
from loft.conf.Config import loftPID


class LoftEngine(object):
    """
    The loft engine is a wrapper class for all underlying loft functionality. This is the main entry point to the application.
    LOFT provides filtering and transport capabilities for onboard logging to offboard log systems. In summary, loft provides tailing
    functionality to a set of configured log files, filters through the files based on a configured set of regular expressions, and
    makes forwarding decisions based on the configured filters. In addition, loft provides a stateful inspection filter that will
    produce a green/red system status log based on a configured filter list and time to live value.
    """
    def __init__(self):
        object.__init__(self)
        # Getting application logging details
        logging.config.fileConfig(os.getcwd() + '/conf/LoftLogConfig')
        self.logger = logging.getLogger()
        # PID for an init script to note
        self.loftPID = loftPID

    def set_pid_file(self, pid_file):
        #create a pid file
        p = open(pid_file, 'w')
        pid = str(os.getpid())
        p.write(pid)
        self.logger.info('loft started. Process ID: ' + pid)
        p.flush()
        p.close()
        return

    def main(self):
        self.set_pid_file(self.loftPID)

        #set up queues
        raw_queue = Queue.Queue()
        outQueue = Queue.Queue()

        #start producer
        m = Producer.Producer(outQueue)
        m.daemon = True
        m.start()

        #start tailers
        for log in logFileNames:
            #start a new tailer
            t = Tailer.FileTailer(raw_queue, log)
            t.daemon = True
            t.start()
            self.logger.info(t)
            self.logger.info('Queue size: ' + str(raw_queue.qsize()))

        #start filter engine
        FilterEngine.Filter(raw_queue, outQueue)


if __name__ == "__main__":
    loft = LoftEngine()
    loft.main()
