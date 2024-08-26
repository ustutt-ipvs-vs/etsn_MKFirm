import argparse
import os
from eTSN import eTSN
from eTSN.schedulingStructs import SchedulingParameters
from network.network_graph import NetworkGraph
from scenario.scenario import Scenario

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--network", type=str, help="Path to the network graph file", required=True)
parser.add_argument("-t", "--tt_streams", type=str, help="Path to the tt streams file", required=True)
parser.add_argument("-e", "--et_streams", type=str, help="Path to the et streams file", required=True)
parser.add_argument("-v", "--verbose", help="print a lot of debug outputs. Is overwritten by the raw flag.",
                    action='store_true')
parser.add_argument("--raw-output", help="If set, the output will be in a raw format. Overwrites the verbose flag.",
                    action='store_true')
parser.add_argument("-o", "--output", type=str, help="Path to the output file", default='transmission_output.json')
parser.add_argument("--cplex", type=str, help="Path to cplex executable", default=None)
parser.add_argument("--threads", type=int, help="Number of threads to be used at most", default=4)
parser.add_argument("--timelimit", type=int,
                    help="solver time limit in seconds. Use negative values for unlimited.", default=120)

args = parser.parse_args()
raw_output = args.raw_output
verbose = args.verbose if not raw_output else False

network = NetworkGraph(args.network)
scenario = Scenario(network, args.tt_streams, args.et_streams)

parameters = SchedulingParameters(args)

result = eTSN.solve_scheduling(parameters)

if '/' in str(args.output) and not os.path.isdir(os.path.basename(args.output)):
    os.makedirs(os.path.basename(args.output), exist_ok=True)
# write_result_to_json(result, parameters, args.output)
