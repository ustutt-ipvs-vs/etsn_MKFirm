import argparse
from dataclasses import dataclass
from typing import Dict, List, Tuple
from math import ceil

from docplex.cp import expression
from docplex.cp.expression import CpoIntervalVar, CpoIntVar

import Util
from network.network_elements import EgressPort
from network.network_graph import NetworkGraph
from scenario.scenario import Scenario
from scenario.streamStructs import Stream, StreamType

# stream (with tuple as id), frame_cycle_number, egress_port_id -> List of transmission opportunities
F_type = Dict[Tuple[int, int], Dict[int, Dict[int, List[CpoIntervalVar]]]]
# egress_port_id, stream (with tuple id), frame_cycle_number -> queuing time
Q_type = Dict[int, Dict[Tuple[int, int], Dict[int, CpoIntervalVar]]]
PCP_assignment = Dict[int, CpoIntVar]


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
        self.scenario = Scenario(self.network, args.tt_streams, args.et_streams, args.N)
        self.cplex_executable = args.cplex
        self.timeout = args.timelimit
        self.threads = args.threads
        self.verbose = args.verbose
        self.raw_output = args.raw_output


class CpVariables:
    """Variables for the constraint programming model."""

    # transmission variables (F in the paper)
    _F_tt: F_type
    _F_et: F_type

    # queuing variables for frame isolation (not properly defined in the paper)
    _Q_tt: Q_type = {}
    _Q_et: Q_type = {}

    tt_pcp: PCP_assignment

    def __init__(self, parameters: SchedulingParameters):
        for node in parameters.network.nodes.values():
            for port in node.ports:
                self._Q_tt[port.id] = {}
                self._Q_et[port.id] = {}

        # initialize the variables
        self.prudent_slot_reservation(parameters.scenario)

        # create the et stream variables
        self.create_et_transmission_variables(parameters.scenario)

        # create the PCP variables
        self.create_pcp_variables(parameters.scenario)

    def Q(self, stream_type: StreamType):
        if stream_type == StreamType.ET:
            return self._Q_et
        else:
            return self._Q_tt

    def F(self, stream: Stream):
        if stream.stream_type == StreamType.ET:
            return self._F_et[stream.get_id()]
        else:
            return self._F_tt[stream.get_id()]

    def F_tt_id(self, stream_id_tuple: Tuple[int, int]):
        return self._F_tt[stream_id_tuple]

    def prudent_slot_reservation(self, scenario: Scenario):
        # stream, frame_cycle_number, egress_port_id -> List of transmission opportunities
        self._F_tt: F_type = {}

        for tt_stream in scenario.tt_streams:
            self._F_tt[tt_stream.get_id()] = {}

            for frame_cycle_number in Util.iterate_frames_per_hc(tt_stream, scenario.hyper_cycle):
                self._F_tt[tt_stream.get_id()][frame_cycle_number] = {}

                for egress_port in tt_stream.route:
                    T = egress_port.calculate_transmission_delay_in_ns_of(
                        tt_stream.frame_size_byte) + egress_port.get_inter_frame_gap()

                    period_start = frame_cycle_number * tt_stream.cycle_time_ns
                    period_end = period_start + tt_stream.cycle_time_ns

                    frames_on_link: List[CpoIntervalVar] = [expression.interval_var(
                        start=(period_start, period_end),
                        end=(period_start, period_end),
                        length=T,
                        name=f"stream_{tt_stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}_#{0}")]

                    for et_stream in scenario.et_streams:
                        if et_stream.get_id()[1] != 0:
                            # skip, since every et stream should be considered only once (with the probability_number = 0)
                            continue
                        s_e_T = et_stream.min_inter_event_time_ns
                        if egress_port in et_stream.route:

                            # since we assume equal frame sizes, we can skip parts of the computation
                            n = ceil(T / s_e_T)
                            # reserve the slot for the et stream
                            for i in range(n):  # +1 since we need also one slot for the tt stream
                                frames_on_link.append(expression.interval_var(
                                    start=(period_start, period_end),
                                    end=(period_start, period_end),
                                    length=T,
                                    name=f"stream_{tt_stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}_#{len(frames_on_link)}",
                                    optional=False))
                    self._F_tt[tt_stream.get_id()][frame_cycle_number][egress_port.id] = frames_on_link

                    self._Q_tt.setdefault(egress_port.id, {}).setdefault(tt_stream.get_id(), {})[
                        frame_cycle_number] = expression.interval_var(
                        start=(period_start, period_end),
                        end=(period_start, period_end),
                        name=f"queuing_tt_stream_{tt_stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}",
                        optional=False)
                    # end of route loop
                # end of frame loop
            # end of tt stream loop

    def create_et_transmission_variables(self, scenario: Scenario):
        self._F_et: F_type = {}
        for et_stream in scenario.et_streams:
            self._F_et[et_stream.get_id()] = {}
            for frame_cycle_number in Util.iterate_frames_per_hc(et_stream, scenario.hyper_cycle):

                period_start = frame_cycle_number * et_stream.min_inter_event_time_ns
                release_time = period_start + et_stream.occurrence_time_ns
                period_end = period_start + et_stream.min_inter_event_time_ns

                self._F_et[et_stream.get_id()][frame_cycle_number] = {}
                egress_port: EgressPort
                for egress_port in et_stream.route:
                    # transmission variable
                    self._F_et[et_stream.get_id()][frame_cycle_number][egress_port.id] = [expression.interval_var(
                        start=(release_time, period_end),
                        end=(release_time, period_end),
                        length=egress_port.calculate_transmission_delay_in_ns_of(
                            et_stream.frame_size_byte) + egress_port.get_inter_frame_gap(),
                        name=f"et_stream_{et_stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}_N={et_stream.probabilistic_stream_number}",
                        optional=False)]
                    # queuing variable (to ensure frame isolation)
                    self._Q_et.setdefault(egress_port.id, {}).setdefault(et_stream.get_id(), {})[
                        frame_cycle_number] = expression.interval_var(
                        start=(release_time, period_end),
                        end=(release_time, period_end),
                        name=f"queuing_et_stream_{et_stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}_N={et_stream.probabilistic_stream_number}",
                        optional=False
                    )

    def create_pcp_variables(self, scenario: Scenario):
        self.tt_pcp: PCP_assignment = {}

        for tt_stream in scenario.tt_streams:
            self.tt_pcp[tt_stream.get_pure_stream_id()] = expression.integer_var(0, 6,
                                                                                 f"pcp_tt_{tt_stream.get_pure_stream_id()}")
