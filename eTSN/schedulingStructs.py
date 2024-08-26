from dataclasses import dataclass

from network.network_graph import NetworkGraph
from scenario.scenario import Scenario


@dataclass
class SchedulingParameters:
    """Parameters for the scheduling model."""
    network: NetworkGraph
    scenario: Scenario

    verbose: bool
    raw_output: bool
