import unittest

from Util import get_frames_per_hc, iterate_frames_per_hc
from scenario.scenario import Stream
from scenario.streamStructs import ETStream, TTStream


class TestUtil(unittest.TestCase):

    def test_get_frames_per_hc(self):
        s1: Stream = TTStream(None)
        s1.cycle_time_ns = 1000

        self.assertEqual(get_frames_per_hc(s1, 1000), 1)
        self.assertEqual(get_frames_per_hc(s1, 5000), 5)
        self.assertEqual(get_frames_per_hc(s1, 100000), 100)

        s2: Stream = ETStream(None)
        s2.min_inter_event_time_ns = 5000

        self.assertEqual(get_frames_per_hc(s2, 5000), 1)
        self.assertEqual(get_frames_per_hc(s2, 100000), 20)

        s3: Stream = TTStream(None)
        s3.cycle_time_ns = 0

        self.assertRaises(ZeroDivisionError, get_frames_per_hc, s3, 1000)

    def test_iterate_frames_per_hc(self):
        s1: Stream = TTStream(None)
        s1.cycle_time_ns = 1000

        self.assertEqual(list(iterate_frames_per_hc(s1, 1000)), [0])
        self.assertEqual(list(iterate_frames_per_hc(s1, 5000)), [0, 1, 2, 3, 4])
        self.assertEqual(list(iterate_frames_per_hc(s1, 100000)), list(range(0, 100)))

        s2: Stream = ETStream(None)
        s2.min_inter_event_time_ns = 5000

        self.assertEqual(list(iterate_frames_per_hc(s2, 5000)), [0])
        self.assertEqual(list(iterate_frames_per_hc(s2, 100000)), list(range(0, 20)))

        s3: Stream = TTStream(None)
        s3.cycle_time_ns = 0

        self.assertRaises(ZeroDivisionError, iterate_frames_per_hc, s3, 1000)
