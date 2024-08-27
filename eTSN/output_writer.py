import json
import os
from typing import List

from docplex.cp.solution import CpoSolveResult

from eTSN.schedulingStructs import SchedulingParameters


def create_result_structure(e_tsn_result: CpoSolveResult, parameters: SchedulingParameters) -> List[any]:
    # TODO implement this function
    return []


def write_result_to_json(e_tsn_result: CpoSolveResult, parameters: SchedulingParameters, output_file: str):
    # create directory, if needed
    if '/' in str(output_file) and not os.path.isdir(os.path.basename(output_file)):
        os.makedirs(os.path.basename(output_file), exist_ok=True)

    result_structure = create_result_structure(e_tsn_result, parameters)
    with open(output_file, 'w') as file:
        json.dump(result_structure, file, indent=4)
