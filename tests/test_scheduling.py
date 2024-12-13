from argparse import Namespace
import unittest
import json

from eTSN import eTSN
from eTSN.output_writer import write_result_to_json
from eTSN.schedulingStructs import SchedulingParameters


class TestScenario(unittest.TestCase):

    def test_scheduling(self):
        output_path: str = 'tests/test_data/sample_input/test_transmission_output.json'
        args = Namespace(network='tests/test_data/sample_input/topology.json', tt_streams='tests/test_data/sample_input/streams.json', 
                         et_streams='tests/test_data/sample_input/emergency_streams.json', verbose=False, raw_output=False, output=output_path, cplex=None, threads=4, timelimit=120, N=1)
        parameters = SchedulingParameters(args)
        result = eTSN.solve_scheduling(parameters)
        write_result_to_json(result, parameters, output_path)
       
        with open(output_path) as result_file:
            result_json = json.load(result_file)
            # stream count
            self.assertEqual(len(result_json), len(parameters.scenario.get_tt_stream_ids()))
            
    def test_scheduling_infeasible(self):
        output_path: str = 'tests/test_data/sample_input/test_transmission_output.json'
        args = Namespace(network='tests/test_data/sample_input/topology.json', tt_streams='tests/test_data/sample_input/streams.json', 
                         et_streams='tests/test_data/sample_input/emergency_streams_infeasible.json', verbose=False, raw_output=False, output=output_path, cplex=None, threads=4, timelimit=120, N=1)
        parameters = SchedulingParameters(args)
        result = eTSN.solve_scheduling(parameters)
        
        self.assertEqual(result.is_solution(), False)
