from itertools import pairwise, combinations, product, chain
from typing import List

from docplex.cp.expression import CpoIntervalVar
from docplex.cp.model import CpoModel
from docplex.cp.modeler import *
from docplex.cp.solution import CpoSolveResult

import Util
from eTSN.schedulingStructs import SchedulingParameters, CpVariables
from network.network_elements import EgressPort
from scenario.streamStructs import Stream, ETStream, StreamType


def solve_scheduling(parameters: SchedulingParameters) -> CpoSolveResult:
    variables = CpVariables(parameters)

    mdl = CpoModel()
    # create constraints (use functions)
    create_time_constraints(mdl, variables, parameters)
    create_frame_overlap_constraints(mdl, variables, parameters)
    # we skip the priority constraints, since we assume there are no TT streams with prio higher than ET streams
    create_adjacent_link_constraints(mdl, variables, parameters)
    create_frame_isolation_constraints(mdl, variables, parameters)

    # create the optimization goal (use a function)

    # call the actual planning
    result = planning(mdl, parameters)

    return result


def create_time_constraints(mdl: CpoModel, variables: CpVariables, param: SchedulingParameters):
    """
    create the time constraints Section IV.B.1) of the paper
    :param mdl:
    :param variables:
    :param param:
    :return:
    """

    # (1) transmission within period:
    # the non-negative phases part is left out, since the interval variables are already limited to non-negative values
    # the constraint ensuring the transmission is within the period is also left out, since we already limit the interval
    # variables accordingly, when creating them.

    # (2) first transmission after occurrence time for ET streams: skipped, since we do not have an occurrence time

    # (3) multiple transmission opportunities precedence:
    def define_transmission_opportunity_precedence(stream: Stream):
        """
        Multiple transmissions of one stream (within the same period) must be in order
        :param stream:
        :return:
        """
        for frame_cycle_number in Util.iterate_frames_per_hc(stream, param.scenario.hyper_cycle):
            for egress_port in stream.route:
                transmission_opportunities = variables.F(stream)[frame_cycle_number][egress_port.id]
                for first_tx, second_tx in pairwise(transmission_opportunities):
                    mdl.add_constraint(end_before_start(first_tx, second_tx))

    # (4) deadline constraint:
    def define_deadline_constraint(stream: Stream):
        """
        Define the deadline constraint for a stream, i.e., the last transmission opportunity must be within the deadline
        :param stream: Stream Object
        :return:
        """
        for frame_cycle_number in Util.iterate_frames_per_hc(stream, param.scenario.hyper_cycle):
            last_link = stream.route[-1]
            for transmission_opportunity in variables.F(stream)[frame_cycle_number][last_link.id]:
                actual_deadline = frame_cycle_number * stream.get_period() + stream.occurrence_time_ns + stream.deadline_ns
                # the propagation delay is not considered in the paper. We add it for correctness.
                mdl.add_constraint(
                    end_of(transmission_opportunity) + last_link.propagation_delay_ns <= actual_deadline)

    # apply the constraints to the streams
    for tt_stream in param.scenario.tt_streams:
        define_transmission_opportunity_precedence(tt_stream)
        define_deadline_constraint(tt_stream)

    for et_stream in param.scenario.et_streams:
        define_transmission_opportunity_precedence(et_stream)
        define_deadline_constraint(et_stream)


def create_frame_overlap_constraints(mdl: CpoModel, variables: CpVariables, param: SchedulingParameters):
    """
    create the frame overlap constraints Section IV.B.2) of the paper
    :param mdl:
    :param variables:
    :param param:
    :return:
    """
    # (5) frame overlap constraint:
    # The TT transmissions must not overlap
    for node in param.network.nodes.values():
        for egress_port in node.ports:
            transmission_list: List[CpoIntervalVar] = []
            for tt_stream in [s for s in param.scenario.tt_streams if egress_port in s.route]:
                for frame_cycle_number in Util.iterate_frames_per_hc(tt_stream, param.scenario.hyper_cycle):
                    transmission_list.extend(variables.F(tt_stream)[frame_cycle_number][egress_port.id])
            if len(transmission_list) > 1:
                mdl.add_constraint(no_overlap(transmission_list))

    # An ET transmission must not overlap with any ET transmission from a different ET stream
    et_stream_a: ETStream
    et_stream_b: ETStream
    for et_stream_a, et_stream_b in combinations(param.scenario.et_streams, r=2):
        if et_stream_a.get_pure_stream_id() == et_stream_b.get_pure_stream_id():
            # a and b are different probabilistic streams of the same ET stream
            continue
        shared_egress_ports = set(et_stream_a.route).intersection(et_stream_b.route)
        for egress_port in shared_egress_ports:
            transmissions_a = chain(*[variables.F(et_stream_a)[key][egress_port.id] for key in
                                      variables.F(et_stream_a).keys()])
            transmissions_b = chain(
                *[variables.F(et_stream_b)[key][egress_port.id] for key in
                  variables.F(et_stream_b).keys()])
            for tx_a, tx_b in product(transmissions_a, transmissions_b):
                mdl.add_constraint(no_overlap([tx_a, tx_b]))


def create_adjacent_link_constraints(mdl: CpoModel, variables: CpVariables, param: SchedulingParameters):
    """
    create the adjacent link constraints Section IV.B.4) of the paper
    :param mdl:
    :param variables:
    :param param:
    :return:
    """

    # (7) adjacent link constraint:
    def define_adjacent_link_constraint(stream: Stream):
        """
        Define the adjacent link constraint for a stream, i.e., the transmissions must be in order
        :param stream: Stream Object
        :return:
        """
        for frame_cycle_number in Util.iterate_frames_per_hc(stream, param.scenario.hyper_cycle):
            hop_i: EgressPort
            hop_i_plus_1: EgressPort
            for hop_i, hop_i_plus_1 in pairwise(stream.route):
                last_transmission_on_i = variables.F(stream)[frame_cycle_number][hop_i.id][-1]
                first_transmission_on_i_plus_1 = variables.F(stream)[frame_cycle_number][hop_i_plus_1.id][0]
                mdl.add_constraint(end_before_start(last_transmission_on_i, first_transmission_on_i_plus_1,
                                                    delay=hop_i.propagation_delay_ns + param.network.get_node(
                                                        hop_i_plus_1.host_node).processing_delay_ns))

    for tt_stream in param.scenario.tt_streams:
        define_adjacent_link_constraint(tt_stream)
    for et_stream in param.scenario.et_streams:
        define_adjacent_link_constraint(et_stream)


def create_frame_isolation_constraints(mdl: CpoModel, variables: CpVariables, param: SchedulingParameters):
    """
    create the frame isolation constraints, barely mentioned in the paper in Section IV.B.3)
    :param mdl:
    :param variables:
    :param param:
    :return:
    """

    def define_interval_borders(stream: Stream):
        # also works as a precedence constraint in a way.
        for frame_cycle_number in Util.iterate_frames_per_hc(stream, param.scenario.hyper_cycle):
            previous_egress_port: EgressPort | None = None
            for egress_port in stream.route:
                queuing_var = variables.Q(stream.stream_type)[egress_port.id][stream.get_id()][frame_cycle_number]
                transmission_list = variables.F(stream)[frame_cycle_number][egress_port.id]
                # queuing starts at the arrival of the first transmission slot at the current link
                if previous_egress_port is None:
                    # first hop, just start the queuing at the start of the first transmission slot
                    mdl.add_constraint(start_at_start(queuing_var, transmission_list[0]))
                else:
                    # consecutive hop, queuing starts at the end of the previous transmission slot + delays
                    # Note: use the first transmission slot [0], since it is the earliest opportunity
                    mdl.add_constraint(
                        end_at_start(variables.F(stream)[frame_cycle_number][previous_egress_port.id][0],
                                     queuing_var,
                                     delay=previous_egress_port.propagation_delay_ns + param.network.get_node(
                                         egress_port.host_node).processing_delay_ns))

                # queuing ends at the end of the latest transmission slot
                mdl.add_constraint(end_at_end(queuing_var, transmission_list[-1]))
                previous_egress_port = egress_port

    def define_no_overlap_constraints_tt():
        for egress_port_dict in variables.Q(StreamType.TT).values():
            '''
            for every link
                for every stream combination
                    for every cycle combination
                        filter all combinations where the start/end values are definitely in a different period
                        add a no_overlap constraint IF the pcp value is the same
            '''
            for stream_a, stream_b in combinations(egress_port_dict.keys(), r=2):
                for cycle_a, cycle_b in product(egress_port_dict[stream_a].keys(), egress_port_dict[stream_b].keys()):
                    interval_a = egress_port_dict[stream_a][cycle_a]
                    interval_b = egress_port_dict[stream_b][cycle_b]
                    if interval_a.get_end()[1] <= interval_b.get_start()[0] or interval_a.get_start()[0] >= \
                            interval_b.get_end()[1]:
                        # start and end are intervals, hence we need 0 to get the start of the interval and 1 # to get the end of the interval
                        continue
                    '''
                    3 cases:
                    1) pcp_a == pcp_b
                        -> no overlap
                    2) pcp_a < pcp_b
                        -> no overlap if start_a <= start_b
                    3) pcp_a > pcp_b
                        -> no overlap if start_b <= start_a
                        
                    2 and 3 ensure that a stream with a higher pcp value cannot overtake the earlier stream. 
                    '''
                    mdl.add_constraint(if_then(
                        variables.tt_pcp[stream_a[0]] == variables.tt_pcp[stream_b[0]],
                        # no_overlap does not return a bool, so we need to check manually
                        logical_or(end_of(interval_a) <= start_of(interval_b),
                                   end_of(interval_b) <= start_of(interval_a))
                        # could be less strict, if we get the start of the last transmission slot. However, not part of eTSN
                    ))
                    mdl.add_constraint(if_then(
                        logical_and(
                            variables.tt_pcp[stream_a[0]] < variables.tt_pcp[stream_b[0]],
                            start_of(interval_a) <= start_of(interval_b)
                        ),
                        # no_overlap does not return a bool, so we need to check manually
                        end_of(interval_a) <= start_of(interval_b)
                        # could be less strict, if we get the start of the last transmission slot. However, not part of eTSN
                    ))
                    mdl.add_constraint(if_then(
                        logical_and(
                            variables.tt_pcp[stream_b[0]] < variables.tt_pcp[stream_a[0]],
                            start_of(interval_b) <= start_of(interval_a)
                        ),
                        # no_overlap does not return a bool, so we need to check manually
                        end_of(interval_b) <= start_of(interval_a)
                        # could be less strict, if we get the start of the last transmission slot. However, not part of eTSN
                    ))

    def define_no_overlap_constraints_et():
        for egress_port_dict in variables.Q(StreamType.ET).values():
            '''
            for every link
                for every stream combination
                    for every cycle combination
                        filter all combinations where the stream id is the same (probabilistic streams of the same stream)
                        add a no_overlap constraint
            '''
            for stream_a, stream_b in combinations(egress_port_dict.keys(), r=2):
                if stream_a[0] == stream_b[0]:
                    continue
                for cycle_a, cycle_b in product(egress_port_dict[stream_a].keys(), egress_port_dict[stream_b].keys()):
                    interval_a = egress_port_dict[stream_a][cycle_a]
                    interval_b = egress_port_dict[stream_b][cycle_b]
                    if interval_a.get_end()[1] <= interval_b.get_start()[0] or interval_a.get_start()[0] >= \
                            interval_b.get_end()[1]:
                        continue
                    mdl.add_constraint(no_overlap([interval_a, interval_b]))

    def ensure_pcp_is_set():
        for stream in param.scenario.tt_streams:
            # this enforces each pcp variable to be set (and to be part of the solution)
            mdl.add_constraint(variables.tt_pcp[stream.get_pure_stream_id()] >= 0)

    # ensure correct interval borders
    for tt_stream in param.scenario.tt_streams:
        define_interval_borders(tt_stream)
    for et_stream in param.scenario.et_streams:
        define_interval_borders(et_stream)

    define_no_overlap_constraints_tt()
    define_no_overlap_constraints_et()
    ensure_pcp_is_set()


def optimization_goal(mdl: CpoModel, variables: CpVariables, param: SchedulingParameters):
    """
    Minimize... # TODO
    """
    '''
    Option 1: feasible solution
    + shorter runtime
    - ET traffic might suffer longer delays
    
    Option 2: minimize the maximum delay of ET traffic
    + ET traffic is prioritized
    - longer runtime
    
    -> for now we go with option 1, i.e., do nothing in here
    '''
    pass


def planning(mdl: CpoModel, param: SchedulingParameters) -> CpoSolveResult:
    start_solving_time = time.time()

    if param.verbose:
        print("Solving model....")
    log_verbosity = 'Quiet' if param.raw_output else 'Terse'
    warning_level = 0 if param.raw_output else 2
    mdl_sol: CpoSolveResult
    if param.cplex_executable:
        mdl_sol = mdl.solve(TimeLimit=param.timeout, Workers=param.threads, LogVerbosity=log_verbosity,
                            WarningLevel=warning_level,
                            execfile=param.cplex_executable)
    else:
        mdl_sol = mdl.solve(TimeLimit=param.timeout, Workers=param.threads, WarningLevel=warning_level,
                            LogVerbosity=log_verbosity)

    end_solving_time = time.time()

    if param.verbose:
        mdl_sol.print_solution()
        print("Solving time: ", end_solving_time - start_solving_time)

    return mdl_sol
