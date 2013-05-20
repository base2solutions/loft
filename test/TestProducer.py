import unittest
import loft.Producer
import Queue
import time
import threading


class TestProducer(unittest.TestCase):

    def setUp(self):
        self.q = Queue.Queue()
        self.q.put("test Queue log 1")
        self.q.put("test Queue log 2")
        self.q.put("test Queue log 3")

        t_stop = threading.Event()
        m = loft.Producer.Producer(self.q, "http://172.31.31.31:8080/prop-service/", t_stop)
        m.daemon = True
        m.start()
        self.q.put("test Queue log 4")
        self.q.put("test Queue log 5")
        self.q.put("test Queue log 6")
        time.sleep(2)
        t_stop.set()


    def test_queueEmpty(self):
        #Queue should be empty after setup as class instantiation should send all
        assert self.q.qsize() == 0


if __name__ == '__main__':
    unittest.main()