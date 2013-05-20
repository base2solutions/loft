import logging
import threading
from loft.conf.Config import outputMethod


class Producer(threading.Thread):
    def __init__(self, queue, stopEvent=threading.Event()):
        """
        Initializes Msg Queue.
        :param queue: Queue containing filtered messages to produce
        :param stopEvent: Event to stop the queue
        """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self._queue = queue
        self._sequenceId = 0
        self._stopEvent = stopEvent

    def run(self):
        """
        Send the messages while stop hasn't been called
        """
        #start sending messages
        while not self._stopEvent.is_set():
            self.__postToProducer(self._queue.get())

    def __postToProducer(self, msg):
        """
        Posts message according to implemented logic
        :param msg: msg to send through producer
        """
        outputMethod(msg)






