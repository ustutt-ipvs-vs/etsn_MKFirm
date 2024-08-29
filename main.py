import argparse
from eTSN import eTSN
from eTSN.output_writer import write_result_to_json
from eTSN.schedulingStructs import SchedulingParameters

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--network", type=str, help="Path to the network graph file", required=True)
parser.add_argument("-t", "--tt_streams", type=str, help="Path to the tt streams file", required=True)
parser.add_argument("-e", "--et_streams", type=str, help="Path to the et streams file", required=True)
parser.add_argument("-v", "--verbose", help="print a lot of debug outputs. Is overwritten by the raw flag.",
                    action='store_true')
parser.add_argument("--raw-output", help="If set, the output will be in a raw format. Overwrites the verbose flag.",
                    action='store_true')
parser.add_argument("-o", "--output", type=str, help="Path to the output file")
parser.add_argument("--cplex", type=str, help="Path to cplex executable", default=None)
parser.add_argument("--threads", type=int, help="Number of threads to be used at most", default=4)
parser.add_argument("--timelimit", type=int,
                    help="solver time limit in seconds. Use negative values for unlimited.", default=120)
parser.add_argument("-N", "--N", type=int, help="Number of probabilistic streams", default=1)

args = parser.parse_args()

# actual work starts here
parameters = SchedulingParameters(args)
result = eTSN.solve_scheduling(parameters)
write_result_to_json(result, parameters, args.output)
