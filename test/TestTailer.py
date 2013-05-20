
import unittest
import loft.Tailer
import Queue
import time
import threading


class TestTailer(unittest.TestCase):

    def test_threadStart(self):
        m1_stop = threading.Event()
        m2_stop = threading.Event()
        g_stop = threading.Event()
        raw_queue = Queue.Queue()
        m1 = loft.Tailer.FileTailer(raw_queue, r'../test/messagesTail', m1_stop)
        m1.daemon = True
        m1.start()
        print (m1)

        m2 = loft.Tailer.FileTailer(raw_queue, r'../test/messages-20130403', m2_stop)
        m2.daemon = True
        m2.start()
        print (m2)
        self.assertTrue(m1.isAlive())
        self.assertTrue(m2.isAlive())
        self.assertTrue(raw_queue.qsize() != 0)

        time.sleep(1)
        m1_stop.set()
        m2_stop.set()
        time.sleep(1)

        self.assertFalse(m1.isAlive())
        self.assertFalse(m2.isAlive())

        g = loft.Tailer.getFile(raw_queue, g_stop)
        g.daemon = True
        g.start()
        print (g)
        self.assertTrue(g.isAlive())
        time.sleep(1)
        g_stop.set()
        time.sleep(1)

        #raw_queue.join()
        print('Raw size: '+ str(raw_queue.qsize()))
        self.assertEqual(raw_queue.qsize(), 0)

if __name__ == '__main__':
    unittest.main()