from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple
from abc import ABC, abstractmethod

from network.network_elements import EgressPort


class StreamType(Enum):
    TT = 1
    ET = 2


@dataclass
class Stream(ABC):
    _stream_id: int
    name: str

    stream_type: StreamType

    source: int
    destination: int
    route: List[EgressPort]
    frame_size_byte: int
    deadline_ns: int
    occurrence_time_ns: int

    def __init__(self, json_stream):
        if json_stream is not None:
            self._stream_id = int(json_stream['id'])
            self.name = json_stream['name']
            self.source = int(json_stream['source'])
            self.destination = int(json_stream['target'])
            self.frame_size_byte = int(json_stream['frame_size_byte'])
            self.occurrence_time_ns = 0

    def get_id(self) -> Tuple[int, int]:
        """
        Get the stream id and the probabilistic stream number. This is to distinguish between different probabilistic streams.
        For TT streams the probabilistic stream number is always 0.
        :return:
        """
        return self._stream_id, 0

    def get_pure_stream_id(self):
        """
        Get the stream id without the probabilistic stream number. I.e., the id a user would expect.
        :return:
        """
        return self._stream_id

    @abstractmethod
    def get_period(self):
        pass


@dataclass
class TTStream(Stream):
    stream_type = StreamType.TT
    cycle_time_ns: int

    def __init__(self, tt_stream):
        super().__init__(tt_stream)
        self.cycle_time_ns = int(tt_stream['cycle_time_ns'])
        self.deadline_ns = int(tt_stream['deadline_ns'])

    def get_period(self):
        return self.cycle_time_ns


@dataclass
class ETStream(Stream):
    stream_type = StreamType.ET
    ttStreamID: int
    min_inter_event_time_ns: int

    json_route: List[any]
    probabilistic_stream_number: int
    occurrence_time_ns: int

    def __init__(self, et_stream, probabilistic_stream_number: int = 0, N: int = 1):
        super().__init__(et_stream)
        self.ttStreamID = int(et_stream['ttStreamID'])
        self.min_inter_event_time_ns = int(et_stream['min_inter_event_time_ns'])
        self.json_route = et_stream['route']
        # TODO maybe we need a better value here. E.g., as part of the data generation.
        self.deadline_ns = int(self.min_inter_event_time_ns / 2)

        self.probabilistic_stream_number = probabilistic_stream_number
        self.occurrence_time_ns = int(self.min_inter_event_time_ns * self.probabilistic_stream_number / N)

    def get_period(self):
        return self.min_inter_event_time_ns

    def get_id(self) -> Tuple[int, int]:
        return self._stream_id, self.probabilistic_stream_number
