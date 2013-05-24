import Queue
import re
import sys
import time
import logging
from loft.conf.Filters import stateInspector
from loft.conf.Filters import outgoingFilter
from loft.conf.Filters import stateStatusMsgMet
from loft.conf.Filters import stateStatusMsgNotMet
from loft.conf.Config import ttl
from threading import Timer

class Filter(object):

    def __init__(self, inQueue, outQueue, stateInspectorDict=stateInspector, outputFilterDict=outgoingFilter, stateInspectorTTL=ttl, runOnce=False):
        """
        Starts the filtering engine. Provides system health check and log forwarding decisions based on configured filters.
        :param inQueue: Filter input queue. This queue should contain the raw unfiltered messages from the log tailers.
        :param outQueue: Filter output queue. This queue will contain the filtered messages for sending to the prop service.
        :param stateInspectorDict: Smart filter regex dictionary. By default this is read out of configuration.
        :param outputFilterDict: Dumb filter regex dictionary. By default this is read out of configuration.
        :param stateInspectorTTL: Smart filter time to live for system health check in seconds. By default this is read out of configuration.
        :param runOnce: Will run the filter once. False by default - should remain false for normal system usage. Used for testing.
        """
        object.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.stateInspectorDict = self.__sortRegexDict(stateInspectorDict)
        self.outputFilterDict = self.__sortRegexDict(outputFilterDict)
        self.stateInspectorTTL = stateInspectorTTL
        # used for killing the main, but in production it will never die
        self.runOnce = runOnce

        #build the filter objects
        self.stateInspectorList = self.__buildSmartRegexList(self.stateInspectorDict)
        self.outputFilterList = self.__buildDumbRegexList(self.outputFilterDict)

        #set the initialization time
        self.initializationTime = time.time()
        self.inspectorMsgSent = False

        #Schedule the ttl event
        Timer(ttl, self.stateInspectorTtlCheck, ()).start()

        #while True:
        if runOnce is True:
            while self.inQueue.qsize() != 0:
                line = self.inQueue.get()
                self.stateInspector(line, self.stateInspectorTTL)
                self.outputFilter(line)
        else:
            while True:
                #time.sleep(.001) ## here for diagnostics, disable for max performance
                try:
                    line = self.inQueue.get()
                    self.stateInspector(line, self.stateInspectorTTL)
                    self.outputFilter(line)
                except KeyboardInterrupt:
                    #cleanup
                    self.logger.warn('Shut down by keyboard')
                    sys.exit()

    def stateInspectorTtlCheck(self):
        if not self.inspectorMsgSent:
            self.__sendToProducer(stateStatusMsgNotMet)
            self.inspectorMsgSent = True

    def stateInspector(self, logLine, ttl):
        """
        Evaluates a log statement against the filter list and makes a forwarding decision.
        :param logLine: String log message to evaluate
        :param ttl: Timeout in seconds that determines how long the system has to meet its GREEN state.
        """
        #Only filter is health check hasn't been sent
        if not self.inspectorMsgSent:
            for item in self.stateInspectorList:
                if item[0].match(logLine):
                    #update the true/false flag of the tuple
                    item[1] = True
                    break

            #Check the state for all valid or ttl exceeded
            if (time.time() > self.initializationTime + ttl) or (self.__evaluateSmartFilterStatus()):
                #Hit condition that we should send status
                if self.__evaluateSmartFilterStatus() is True:
                    self.__sendToProducer(stateStatusMsgMet)

                #Set some flag to status sent so we don't smartFilter any more
                self.inspectorMsgSent = True

    def outputFilter(self, logLine):
        """
        Evaluates a log statement against the filter list and makes a forwarding decision.
        :param logLine: String log message to evaluate
        """
        for regex in self.outputFilterList:
            if regex.match(logLine):
                self.__sendToProducer(logLine)
                break

    def __evaluateSmartFilterStatus(self):
        """
        Checks to see if smart filters have all been hit and returns true if so. This is the equivalent of a green status.
        """
        #Iterate through the smart filter tuple list
        for tup in self.stateInspectorList:
            if tup[1] is False:
                #If any item is still set to false we haven't met all conditions so return false
                return False

        #If we have successfully iterated through everything and found no false return true
        return True

    def __sortRegexDict(self, regexDict):
        """
        Build an ordered dictionary of regex string values to filter strings against based on a provided dictionary
        :param regexDict: Regex dictionary containing key/regex pairs. The key will be sorted by convention based on
        <filter#>_<filterName>
        """
        orderedRegex = sorted(regexDict.items(), key=lambda t: t[0])
        return orderedRegex

    def __buildDumbRegexList(self, sortedRegexList):
        """
        Builds a list of regex objects in order based on a sorted regex string list
        :param sortedRegexList: Pre-sorted list of regex filter strings.
        """
        regexList = []

        for value in sortedRegexList:
            regexList.append(re.compile(value[1]))

        return regexList

    def __buildSmartRegexList(self, sortedRegexList):
        """
        Builds a list of regex objects and an associated true/false field to track if they have been hit
        :param sortedRegexList: Pre-sorted list of regex filter strings.
        """
        regexList = []
        for value in sortedRegexList:
            item = [re.compile(value[1]), False]
            regexList.append(item)

        return regexList

    def __sendToProducer(self, logMsg):
        """
        Sends a log statement to the message producer
        :param logMsg: String log message to send to the producer
        """
        self.logMsg = logMsg
        self.outQueue.put(logMsg)


def main():
    import Tailer
    from loft.conf.Config import logFileNames
    from loft import Producer


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

    #start filter engine
    Filter(raw_queue, outQueue)

if __name__ == "__main__":
    main()
