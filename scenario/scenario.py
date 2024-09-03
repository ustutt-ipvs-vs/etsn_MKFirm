import json
import math
from dataclasses import dataclass
from typing import Set, List

import Routing
from network.network_graph import NetworkGraph
from scenario.streamStructs import *


@dataclass
class Scenario:
    tt_streams: List[TTStream]
    et_streams: List[ETStream]
    hyper_cycle: int

    def __init__(self, network: NetworkGraph, tt_streams_path: str, et_streams_path: str, N: int = 1):
        self.tt_streams = []
        with open(tt_streams_path) as scenario_file:
            periods: Set[int] = set()
            # create stream objects
            for json_stream in json.load(scenario_file):
                tt_stream = TTStream(json_stream)
                tt_stream.route = Routing.get_dijkstra_shortest_path(tt_stream.source,
                                                                     tt_stream.destination,
                                                                     network,
                                                                     tt_stream.frame_size_byte)
                self.tt_streams.append(tt_stream)
                periods.add(tt_stream.cycle_time_ns)

        self.hyper_cycle = math.lcm(*periods)

        self.et_streams = []
        with open(et_streams_path) as scenario_file:
            # create stream objects
            for json_stream in json.load(scenario_file):
                for probabilistic_stream_number in range(N):
                    et_stream = ETStream(json_stream, probabilistic_stream_number, N)
                    et_stream.route = Routing.get_route_from_json(et_stream, network)
                    self.et_streams.append(et_stream)

    def get_et_stream_ids(self) -> List[Tuple[int, int]]:
        return [stream.get_id() for stream in self.et_streams]

    def get_tt_stream_ids(self) -> List[Tuple[int, int]]:
        return [stream.get_id() for stream in self.tt_streams]

    def get_stream_ids(self) -> List[Tuple[int, int]]:
        return self.get_tt_stream_ids() + self.get_et_stream_ids()
