import unittest
import loft.Tailer
import loft.FilterEngine
import Queue
import time
import threading

class TestTailer(unittest.TestCase):
    def setUp(self):
        self.raw_queue = Queue.Queue()
        self.outQueue = Queue.Queue()
        self.m_stop = threading.Event()
        self.m = loft.Tailer.FileTailer(self.raw_queue, r'../test/messagesTail', self.m_stop)
        self.m.daemon = True
        self.m.start()
        print (self.m)
        time.sleep(1)

    def test_throughput(self):
        self.assertTrue(self.m.isAlive())
        print(self.raw_queue.qsize())
        #Get the input size
        input = (self.raw_queue.qsize())
        self.assertTrue(self.raw_queue.qsize() != 0)
        time.sleep(1)
        self.m_stop.set()
        time.sleep(1)
        self.assertFalse(self.m.isAlive())
        loft.FilterEngine.Filter(inQueue=self.raw_queue, outQueue=self.outQueue, runOnce=True )
        self.assertTrue(self.raw_queue.qsize() == 0)
        self.assertEqual(self.outQueue.qsize(), input)


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.smartFilter = {
            '25_fifth_condition': 'fifth regex',
            '10_second_condition': 'second regex',
            '15_third_condition': 'third regex',
            '05_first_condition': 'some regex',
            '20_fourth_condition': 'fourth regex',
        }

        self.expectedOrder = [
            ('05_first_condition', 'some regex'),
            ('10_second_condition', 'second regex'),
            ('15_third_condition', 'third regex'),
            ('20_fourth_condition', 'fourth regex'),
            ('25_fifth_condition', 'fifth regex'),
        ]

        self.raw_queue = Queue.Queue()
        self.outQueue = Queue.Queue()

        self.filter = loft.FilterEngine.Filter(self.raw_queue, self.outQueue, runOnce=True)

    def test_sortRegexList(self):
        orderedList = self.filter._Filter__sortRegexDict(self.smartFilter)
        self.assertTrue(orderedList == self.expectedOrder)

    def test_buildDumbRegexList(self):
        regexList = self.filter._Filter__buildDumbRegexList(self.filter._Filter__sortRegexDict(self.smartFilter))
        self.assertTrue(regexList[0].pattern == 'some regex')
        self.assertTrue(regexList[4].pattern == 'fifth regex')

    def test_buildSmartRegexList(self):
        regexList = self.filter._Filter__buildSmartRegexList(self.filter._Filter__sortRegexDict(self.smartFilter))
        t = regexList[0]
        self.assertTrue(t[0].pattern == 'some regex')
        self.assertTrue(t[1] is False)

    def test_smartFilterGreen(self):
        ttl = 300
        #run all the strings through the filter so we should hit a green status
        self.filter.stateInspector('some regex', ttl)
        self.filter.stateInspector('second regex', ttl)
        self.filter.stateInspector('third regex', ttl)
        self.filter.stateInspector('fourth regex', ttl)
        self.filter.stateInspector('fifth regex', ttl)

        self.assertTrue(self.outQueue.get() == 'System health check GREEN')

    def test_smartFilterNotMet(self):
        ttl = 300
        #add just a few matches
        self.filter.stateInspector('some regex', ttl)
        self.filter.stateInspector('second regex', ttl)
        self.filter.stateInspector('third regex', ttl)

        #should have nothing in queue
        self.assertTrue(self.outQueue.empty())

    def test_smartFilterRed(self):
        ttl = 2
        #add just a few matches
        self.filter.stateInspector('some regex', ttl)
        self.filter.stateInspector('second regex', ttl)
        self.filter.stateInspector('third regex', ttl)

        #sleep 2 seconds
        time.sleep(3)

        #try a fourth filter - should be after ttl
        self.filter.stateInspector('fourth regex', ttl)

        #should have red status in the queue
        self.assertTrue(self.outQueue.get() == 'System health check RED')

if __name__ == '__main__':
    unittest.main()


