import unittest

from network.network_graph import NetworkGraph
from scenario.scenario import Stream, Scenario


class TestScenario(unittest.TestCase):

    def test_scenario_loading(self):
        network = NetworkGraph("test_data/routing_graph_1.json")
        scenario: Scenario = Scenario(network, "test_data/test_scenario.json", "test_data/test_et_streams.json")

        self.assertEqual(len(scenario.streams), 4)
        self.assertEqual(scenario.get_stream_ids(), [0, 1, 2, 3])

        self.assertEqual(scenario.hyper_cycle, 12000000)

        stream: Stream
        for stream in scenario.streams:
            if stream.stream_id == 0:
                self.assertEqual(stream.source, 0)
                self.assertEqual(stream.destination, 3)
                self.assertEqual(stream.cycle_time_ns, 3000000)
                self.assertEqual(stream.frame_size_byte, 100)
                self.assertEqual(stream.deadline_ns, 6000000)
            elif stream.stream_id == 1:
                self.assertEqual(stream.source, 3)
                self.assertEqual(stream.destination, 0)
                self.assertEqual(stream.cycle_time_ns, 6000000)
                self.assertEqual(stream.frame_size_byte, 200)
                self.assertEqual(stream.deadline_ns, 6000000)
            elif stream.stream_id == 2:
                self.assertEqual(stream.source, 0)
                self.assertEqual(stream.destination, 3)
                self.assertEqual(stream.cycle_time_ns, 4000000)
                self.assertEqual(stream.frame_size_byte, 100)
                self.assertEqual(stream.deadline_ns, 4000000)
            elif stream.stream_id == 3:
                self.assertEqual(stream.source, 3)
                self.assertEqual(stream.destination, 0)
                self.assertEqual(stream.cycle_time_ns, 6000000)
                self.assertEqual(stream.frame_size_byte, 100)
                self.assertEqual(stream.deadline_ns, 6000000)
