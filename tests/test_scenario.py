import unittest

from network.network_graph import NetworkGraph
from scenario.scenario import Scenario
from scenario.structs import Stream, StreamType, TTStream, ETStream


class TestScenario(unittest.TestCase):

    def test_scenario_loading(self):
        network: NetworkGraph = NetworkGraph("test_data/sample_input/topology.json")
        scenario: Scenario = Scenario(network, "test_data/sample_input/streams.json",
                                      "test_data/sample_input/emergency_streams.json")

        self.assertEqual(len(scenario.streams), 15)
        self.assertEqual(scenario.get_stream_ids(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4])

        self.assertEqual(scenario.hyper_cycle, 1200000)

        stream: Stream
        for stream in scenario.streams:
            if stream.stream_type == StreamType.TT:
                # noinspection PyTypeChecker
                tt_stream: TTStream = stream
                if tt_stream.stream_id == 0:
                    self.assertEqual(tt_stream.source, 3)
                    self.assertEqual(tt_stream.destination, 4)
                    self.assertEqual(tt_stream.cycle_time_ns, 300000)
                    self.assertEqual(tt_stream.frame_size_byte, 100)
                    self.assertEqual(tt_stream.deadline_ns, 300000)
                elif tt_stream.stream_id == 1:
                    self.assertEqual(tt_stream.source, 4)
                    self.assertEqual(tt_stream.destination, 2)
                    self.assertEqual(tt_stream.cycle_time_ns, 100000)
                    self.assertEqual(tt_stream.frame_size_byte, 100)
                    self.assertEqual(tt_stream.deadline_ns, 100000)
                elif tt_stream.stream_id == 8:
                    self.assertEqual(tt_stream.source, 2)
                    self.assertEqual(tt_stream.destination, 5)
                    self.assertEqual(tt_stream.cycle_time_ns, 400000)
                    self.assertEqual(tt_stream.frame_size_byte, 100)
                    self.assertEqual(tt_stream.deadline_ns, 400000)
                elif tt_stream.stream_id == 9:
                    self.assertEqual(tt_stream.source, 5)
                    self.assertEqual(tt_stream.destination, 3)
                    self.assertEqual(tt_stream.cycle_time_ns, 100000)
                    self.assertEqual(tt_stream.frame_size_byte, 100)
                    self.assertEqual(tt_stream.deadline_ns, 100000)
            else:
                # noinspection PyTypeChecker
                et_stream: ETStream = stream
                if et_stream.stream_id == 0:
                    self.assertEqual(et_stream.ttStreamID, 1)
                    self.assertEqual(et_stream.source, 4)
                    self.assertEqual(et_stream.destination, 2)
                    self.assertEqual(et_stream.frame_size_byte, 100)
                    self.assertEqual(et_stream.min_inter_event_time_ns, 200000)
                    self.assertEqual(len(et_stream.route), 2)
                elif et_stream.stream_id == 1:
                    self.assertEqual(et_stream.ttStreamID, 2)
                    self.assertEqual(et_stream.source, 3)
                    self.assertEqual(et_stream.destination, 2)
                    self.assertEqual(et_stream.frame_size_byte, 100)
                    self.assertEqual(et_stream.min_inter_event_time_ns, 600000)
                    self.assertEqual(len(et_stream.route), 2)
                elif et_stream.stream_id == 4:
                    self.assertEqual(et_stream.ttStreamID, 7)
                    self.assertEqual(et_stream.source, 2)
                    self.assertEqual(et_stream.destination, 4)
                    self.assertEqual(et_stream.frame_size_byte, 100)
                    self.assertEqual(et_stream.min_inter_event_time_ns, 200000)
                    self.assertEqual(len(et_stream.route), 2)
