import net
import unittest
from unittest.mock import sentinel, patch, MagicMock


class TestInputConnection(unittest.TestCase):

    @patch("net.multiprocessing.Process", return_value=MagicMock())
    def test_init(self, m_Process):
        obj = net.InputConnection(sentinel.connection)
        self.assertEqual(obj.conn, sentinel.connection)
        self.assertTrue(hasattr(obj, "proc"))
        self.assertEqual(m_Process.call_count, 1)
        self.assertEqual(obj.proc.start.call_count, 1)
        self.assertEqual(obj.proc.join.call_count, 1)
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
