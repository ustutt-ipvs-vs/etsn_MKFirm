from dataclasses import dataclass
from enum import Enum
from typing import List
from abc import ABC

from network.network_elements import EgressPort


class StreamType(Enum):
    TT = 1
    ET = 2


@dataclass
class Stream(ABC):
    stream_id: int
    name: str

    stream_type: StreamType

    source: int
    destination: int
    route: List[EgressPort]
    frame_size_byte: int

    def __init__(self, json_stream):
        if json_stream is not None:
            self.stream_id = int(json_stream['id'])
            self.name = json_stream['name']
            self.source = int(json_stream['source'])
            self.destination = int(json_stream['target'])
            self.frame_size_byte = int(json_stream['frame_size_byte'])
            deadline_ns: int


@dataclass
class TTStream(Stream):
    stream_type = StreamType.TT
    cycle_time_ns: int

    def __init__(self, tt_stream):
        super().__init__(tt_stream)
        self.cycle_time_ns = int(tt_stream['cycle_time_ns'])
        self.deadline_ns = int(tt_stream['deadline_ns'])


@dataclass
class ETStream(Stream):
    stream_type = StreamType.ET
    ttStreamID: int
    min_inter_event_time_ns: int

    def __init__(self, et_stream):
        super().__init__(et_stream)
        self.route = et_stream['route']
        self.ttStreamID = int(et_stream['ttStreamID'])
        self.min_inter_event_time_ns = int(et_stream['min_inter_event_time_ns'])
        # TODO we need better value here. Maybe as aprt of the data generation.
        self.deadline_ns = self.min_inter_event_time_ns / 2
