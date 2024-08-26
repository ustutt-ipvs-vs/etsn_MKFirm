import argparse
from dataclasses import dataclass
from typing import Dict, List, Tuple
from math import ceil

from docplex.cp.expression import CpoIntVar, CpoIntervalVar

from network.network_graph import NetworkGraph
from scenario.scenario import Scenario


@dataclass
class SchedulingParameters:
    """Parameters for the scheduling model."""
    network: NetworkGraph
    scenario: Scenario

    cplex_executable: str
    timeout: int
    threads: int
    verbose: bool
    raw_output: bool

    def __init__(self, args: argparse.Namespace):
        self.network = NetworkGraph(args.network)
        self.scenario = Scenario(self.network, args.tt_streams, args.et_streams)
        self.cplex_executable = args.cplex
        self.timeout = args.timelimit
        self.threads = args.threads
        self.verbose = args.verbose
        self.raw_output = args.raw_output


@dataclass
class CpVariables:
    """Variables for the constraint programming model."""

    # todo create the cp variables here, so that the whole struct can be passed to a solver function

    def __init__(self, parameters: SchedulingParameters):
        # initialize the variables
        pass


def prudent_slot_reservation(scenario: Scenario) -> None:
    # stream, frame_cycle_number, link_id
    F: Dict[int, int, int, CpoIntervalVar] = {}

    for tt_stream in scenario.tt_streams:
        stream_dict = {}
        s_t_l = tt_stream.frame_size_byte

        for frame_cycle_number in range(int(scenario.hyper_cycle / tt_stream.cycle_time_ns)):
            frame_cycle_dict = {}

            for link in tt_stream.route:
                frames_on_link: List[CpoIntervalVar] = [CpoIntervalVar(
                    start=(
                        frame_cycle_number * tt_stream.cycle_time_ns,
                        (frame_cycle_number + 1) * tt_stream.cycle_time_ns),
                    end=(
                        frame_cycle_number * tt_stream.cycle_time_ns,
                        (frame_cycle_number + 1) * tt_stream.cycle_time_ns),
                    length=link.calculate_transmission_delay_in_ns_of(s_t_l),
                    name=f"stream_{tt_stream.stream_id}_frame_{frame_cycle_number}_link_{link.id}_#{0}")]

                for et_stream in scenario.et_streams:
                    s_e_l = et_stream.frame_size_byte
                    s_e_T = et_stream.min_inter_event_time_ns
                    if link in et_stream.route:
                        T = link.calculate_transmission_delay_in_ns_of(tt_stream.frame_size_byte)
                        '''
                        TODO assume all frames have the same size
                        '''
                        n = s_e_l * ceil(s_t_l * (T / s_e_T))
                        # reserve the slot for the et stream
                        for i in range(n):  # +1 since we need also one slot for the tt stream
                            frames_on_link.append(CpoIntervalVar(
                                start=(
                                    frame_cycle_number * tt_stream.cycle_time_ns,
                                    (frame_cycle_number + 1) * tt_stream.cycle_time_ns),
                                end=(
                                    frame_cycle_number * tt_stream.cycle_time_ns,
                                    (frame_cycle_number + 1) * tt_stream.cycle_time_ns),
                                length=link.calculate_transmission_delay_in_ns_of(s_t_l),
                                name=f"stream_{tt_stream.stream_id}_frame_{frame_cycle_number}_link_{link.id}_#{len(frames_on_link)}"))
                frame_cycle_dict[link.id] = frames_on_link
            # TODO continue here
