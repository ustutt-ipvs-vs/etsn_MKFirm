import argparse
from dataclasses import dataclass
from typing import Dict, List

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
