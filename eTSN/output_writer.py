import json
import os
from typing import List

from docplex.cp.solution import CpoSolveResult

import Util
from eTSN.schedulingStructs import SchedulingParameters


def create_result_structure(e_tsn_result: CpoSolveResult, parameters: SchedulingParameters) -> List[any]:
    # TODO implement this function
    output = []
    for stream in parameters.scenario.tt_streams:
        stream_output = {
            "stream_id": stream.get_pure_stream_id(),
            "pcp": 1  # TODO update if we add frame isolation constraints
        }
        frames = []
        for frame_cycle_number in Util.iterate_frames_per_hc(stream, parameters.scenario.hyper_cycle):
            frame_output = {
                "frame_number": frame_cycle_number
            }

            transmissions = []
            for egress_port in stream.route:
                transmission_slot_number = 0
                variable_name = f"stream_{stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}_#{transmission_slot_number}"

                while variable_name in e_tsn_result.solution:
                    transmission_var = e_tsn_result[variable_name]
                    transmissions.append({
                        "link_id": egress_port.id,
                        "link_name": egress_port.name,
                        "source": egress_port.host_node,
                        "target": egress_port.destination_node,
                        "start": transmission_var.start,
                        "end": transmission_var.end
                    })
                    transmission_slot_number += 1
                    variable_name = f"stream_{stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}_#{transmission_slot_number}"
            frame_output["transmissions"] = transmissions
            frames.append(frame_output)
        stream_output["frames"] = frames
        output.append(stream_output)

    return output


def write_result_to_json(e_tsn_result: CpoSolveResult, parameters: SchedulingParameters, output_file: str):
    # create directory, if needed
    if '/' in str(output_file) and not os.path.isdir(os.path.basename(output_file)):
        os.makedirs(os.path.basename(output_file), exist_ok=True)

    result_structure = create_result_structure(e_tsn_result, parameters)
    if parameters.verbose:
        print('result', result_structure)
    if output_file:
        with open(output_file, 'w') as file:
            json.dump(result_structure, file, indent=4)
