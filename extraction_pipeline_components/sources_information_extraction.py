import logging

import numpy as np
import pydicom

from extraction_pipeline_components.storage_objects.rt_plan_storage_classes import LDRBrachyPlan, Sources


def extract_sources_positions(path_to_rt_plan_file):
    open_dicom = pydicom.dcmread(path_to_rt_plan_file)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()
            channel_sequence = json_version_dicom["300A0230"]["Value"][0]["300A0280"]["Value"]
            sources_positions = {}

            for channel in channel_sequence:
                ref_source = channel["300C000E"]["Value"]
                brachy_control_point = channel["300A02D0"]["Value"][0]
                sources_pos = brachy_control_point["300A02D4"]["Value"]
                if "300A0412" in channel.keys():
                    sources_or = brachy_control_point["300A0412"]["Value"]
                else:
                    sources_or = []

                if ref_source not in sources_positions.keys():
                    sources_positions[ref_source] = {"positions": [sources_pos], "orientations": [sources_or]}
                else:
                    sources_positions[ref_source]["positions"].append(sources_pos)
                    sources_positions[ref_source]["orientations"].append(sources_or)

            for ref_source in sources_positions.keys():
                sources_positions[ref_source]["positions"] = np.asarray(sources_positions[ref_source]["positions"])
                sources_positions[ref_source]["orientations"] = np.asarray(
                    sources_positions[ref_source]["orientations"])

            return sources_positions

        return {}

    except KeyError:
        logging.warning(f"There was an issue while extracting source"
                        f"positions for instance {instance_uid} of patient {patient_id}")

        return {}


def extract_sources_context_information(path_to_rt_plan_file):
    open_dicom = pydicom.dcmread(path_to_rt_plan_file)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()
            rt_struct = json_version_dicom["300C0060"]["Value"][0]["00081155"]["Value"]
            source_sequence = json_version_dicom["300A0210"]["Value"]
            sources_dict = {"RTPlanDate": json_version_dicom["300A0006"],
                            "RTPlanTime": json_version_dicom["300A0007"],
                            "RefRtStructUID": rt_struct}

            for sources in source_sequence:
                source_dict = {"SourceIsotopeName": sources["300A0226"]["Value"][0],
                               "ReferenceAirKermaRate": sources["300A022A"]["Value"][0],
                               "SourceStrengthReferenceDate": sources["300A022C"]["Value"][0],
                               "SourceStrengthReferenceTime": sources["300A022E"]["Value"][0],
                               "MaterialID": sources["300A00E1"]["Value"][0]}
                sources_dict[sources["300A00E1"]["Value"][0]] = source_dict

            return sources_dict

        return {}

    except KeyError:
        logging.warning(f"There was an issue while extracting source"
                        f"information for instance {instance_uid} of patient {patient_id}")

        return {}


def extract_all_sources_informations(path_to_rt_plan_file):
    context = extract_sources_context_information(path_to_rt_plan_file)
    positions = extract_sources_positions(path_to_rt_plan_file)
    brachy_plan = LDRBrachyPlan(context["RefRtStructUID"], context["RTPlanDate"], context["RTPlanTime"])
    list_of_sources = []
    for sources in positions.keys():
        source = Sources(context[sources]["SourceIsotopeName"], context[sources]["ReferenceAirKermaRate"],
                         context[sources]["SourceStrengthReferenceDate"],
                         context[sources]["SourceStrengthReferenceTime"], context[sources]["MaterialID"],
                         positions[sources]["positions"], positions[sources]["orientations"], brachy_plan)
        list_of_sources.append(source)

    brachy_plan.add_sources(list_of_sources)

    return brachy_plan
