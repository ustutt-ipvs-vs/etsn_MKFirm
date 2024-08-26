import json
import math
from dataclasses import dataclass
from typing import Set

import Routing
from network.network_graph import NetworkGraph
from scenario.structs import *


@dataclass
class Scenario:
    streams: List[Stream]
    hyper_cycle: int

    def __init__(self, network: NetworkGraph, tt_streams_path: str, et_streams_path: str):
        self.streams = []
        with open(tt_streams_path) as scenario_file:
            periods: Set[int] = set()
            # create stream objects
            for json_stream in json.load(scenario_file):
                tt_stream = TTStream(json_stream)
                tt_stream.route = Routing.get_dijkstra_shortest_path(tt_stream.source,
                                                                     tt_stream.destination,
                                                                     network,
                                                                     tt_stream.frame_size_byte)
                self.streams.append(tt_stream)
                periods.add(tt_stream.cycle_time_ns)

        self.hyper_cycle = math.lcm(*periods)

        with open(et_streams_path) as scenario_file:
            # create stream objects
            for json_stream in json.load(scenario_file):
                self.streams.append(ETStream(json_stream))

    def get_stream_ids(self):
        return [stream.stream_id for stream in self.streams]
