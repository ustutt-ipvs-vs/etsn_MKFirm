from dataclasses import dataclass
from enum import Enum
from typing import List

from network.network_elements import EgressPort


class StreamType(Enum):
    TT = 1
    ET = 2


@dataclass
class Stream:
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


@dataclass
class TTStream(Stream):
    stream_type = StreamType.TT
    cycle_time_ns: int
    deadline_ns: int

    def __init__(self, tt_stream):
        super().__init__(tt_stream)
        self.cycle_time_ns = int(tt_stream['cycle_time_ns'])
        self.deadline_ns = int(tt_stream['deadline_ns'])


@dataclass
class ETStream(Stream):
    stream_type = StreamType.ET

    min_inter_event_time_ns: int
    survival_time_ns: int

    def __init__(self, et_stream):
        super().__init__(et_stream)
        self.route = et_stream['route']
