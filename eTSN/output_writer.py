import json
import os
from typing import List, Dict

from docplex.cp.solution import CpoSolveResult

import Util
from eTSN.schedulingStructs import SchedulingParameters
from scenario.streamStructs import Stream, StreamType


def create_result_structure(e_tsn_result: CpoSolveResult, parameters: SchedulingParameters) -> List[any]:
    output = []

    def create_stream_json(current_stream: Stream, scheduling_result, scheduling_parameters):
        pcp_variable_name = f"pcp_tt_{current_stream.get_pure_stream_id()}"

        stream_output: Dict
        if current_stream.stream_type == StreamType.TT:
            stream_output = {
                "stream_id": current_stream.get_pure_stream_id(),
                "pcp": scheduling_result[pcp_variable_name]
            }
        else:
            id_tuple = current_stream.get_id()
            stream_output = {
                "stream_id": 1000000 + id_tuple[0] * 100 + id_tuple[1],
                "pcp": 7
            }

        frames = []
        for frame_cycle_number in Util.iterate_frames_per_hc(current_stream,
                                                             scheduling_parameters.scenario.hyper_cycle):
            frame_output = {
                "frame_number": frame_cycle_number
            }

            transmissions = []
            for egress_port in current_stream.route:
                transmission_slot_number = 0
                variable_name = f"stream_{current_stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}_#{transmission_slot_number}"

                while variable_name in scheduling_result.solution:
                    transmission_var = scheduling_result[variable_name]
                    transmissions.append({
                        "link_id": egress_port.id,
                        "link_name": egress_port.name,
                        "source": egress_port.host_node,
                        "target": egress_port.destination_node,
                        "start": transmission_var.start,
                        "end": transmission_var.end
                    })
                    transmission_slot_number += 1
                    variable_name = f"stream_{current_stream.get_pure_stream_id()}_frame_{frame_cycle_number}_link_{egress_port.id}_#{transmission_slot_number}"
            frame_output["transmissions"] = transmissions
            frames.append(frame_output)
        stream_output["frames"] = frames
        return stream_output

    for stream in parameters.scenario.tt_streams:
        output.append(create_stream_json(stream, e_tsn_result, parameters))

    for stream in parameters.scenario.et_streams:
        stream_json = create_stream_json(stream, e_tsn_result, parameters)
        output.append(stream_json)

    return output


def write_result_to_json(e_tsn_result: CpoSolveResult, parameters: SchedulingParameters, output_file: str):
    # create directory, if needed
    if '/' in str(output_file) and not os.path.isdir(os.path.dirname(output_file)):
        os.makedirs(os.path.basename(output_file), exist_ok=True)

    result_structure = create_result_structure(e_tsn_result, parameters)
    if parameters.verbose:
        print('result', result_structure)
    if output_file:
        with open(output_file, 'w') as file:
            json.dump(result_structure, file, indent=4)
