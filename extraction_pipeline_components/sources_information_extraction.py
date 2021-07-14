import logging

import numpy as np
import pydicom

from extraction_pipeline_components.storage_objects.rt_plan_storage_classes import LDRBrachyPlan, Sources


def extract_sources_positions(path_to_rt_plan_file: str) -> dict:
    """
    This method extracts all positions and orientations of all source types.
    For instance, if there are two source type, this method will
    have two different position array stored inside two sub dict.
    The structure of the dictionary returned is:
    {"source number": {"positions": 2d array containing positions, "orientations": 2d array containing positions},
     "source number": {"positions": array, "orientations": array},  ...}
     If no orientation are found, the array will simply be empty

    :param path_to_rt_plan_file: path to the rt plan Dicom file
    :return: the dictionary containing positions of every source types
    """
    open_dicom = pydicom.dcmread(path_to_rt_plan_file)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()
            application_setup_sequence = json_version_dicom["300A0230"]["Value"]
            sources_positions = {}
            for application_setups in application_setup_sequence:
                if "300A0280" in application_setups.keys():
                    channel_sequence = application_setups["300A0280"]["Value"]
                    for channel in channel_sequence:
                        ref_source = channel["300C000E"]["Value"][0]
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

            # converting the lists of lists into arrays
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


def extract_sources_context_information(path_to_rt_plan_file) -> dict:
    """
    This method will extract the rt plan context information along
    with each source type context information.
    For instance, if there are two source type, this method will
    have two different source context info stored in two sub dict.
    The structure of the dictionary returned is:
    {rtplan context info, "source number": {source context information},
     "source number": {source context information},  ...}

    :param path_to_rt_plan_file: path to the rt plan Dicom file
    :return: the dictionary containing all the context information
    """
    open_dicom = pydicom.dcmread(path_to_rt_plan_file)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()

            # extracting referenced uids of rt dose, rt plan and rt dose
            # ------------------------------------------------------------
            rt_plan_uid = json_version_dicom["00080018"]["Value"][0]
            if "300C0080" in json_version_dicom.keys():
                rt_dose = str(json_version_dicom["300C0080"]["Value"][0]["00081155"]["Value"][0])
            else:
                rt_dose = None

            if "300C0060" in json_version_dicom.keys():
                rt_struct = str(json_version_dicom["300C0060"]["Value"][0]["00081155"]["Value"][0])
            else:
                rt_struct = None
            # ------------------------------------------------------------

            source_sequence = json_version_dicom["300A0210"]["Value"]
            sources_dict = {"RTPlanDate": str(json_version_dicom["300A0006"]["Value"][0]),
                            "RTPlanTime": float(json_version_dicom["300A0007"]["Value"][0]),
                            "RefRtStructUID": rt_struct, "RefRtDoseUID": rt_dose, "RTPlan": rt_plan_uid}

            for sources in source_sequence:
                source_dict = {"SourceIsotopeName": str(sources["300A0226"]["Value"][0]),
                               "ReferenceAirKermaRate": float(sources["300A022A"]["Value"][0]),
                               "SourceStrengthReferenceDate": str(sources["300A022C"]["Value"][0]),
                               "SourceStrengthReferenceTime": float(sources["300A022E"]["Value"][0]),
                               "MaterialID": str(sources["300A00E1"]["Value"][0]),
                               "SourceType": str(sources["300A0214"]["Value"][0]),
                               "SourceManufacturer": str(sources["300A0216"]["Value"][0]),
                               "ActiveSourceDiameter": float(sources["300A0218"]["Value"][0]),
                               "ActiveSourceLength": float(sources["300A021A"]["Value"][0])}
                sources_dict[sources["300A0212"]["Value"][0]] = source_dict

            return sources_dict

        return {}

    except KeyError:
        logging.warning(f"There was an issue while extracting source"
                        f"information for instance {instance_uid} of patient {patient_id}")

        return {}


def extract_all_sources_informations(path_to_rt_plan_file) -> LDRBrachyPlan or None:
    """
    This method simply uses the output of both extract_sources_positions()
    and extract_sources_context_information() in order to store all the informations
    into a LDRBrachyPlan object and some Sources objects. These objects allow easier
    interactions with all the info.

    :param path_to_rt_plan_file: path to the rt plan Dicom file
    :return: a LDRBrachyPlan object
    """
    context = extract_sources_context_information(path_to_rt_plan_file)
    positions = extract_sources_positions(path_to_rt_plan_file)
    if context == {} or positions == {}:
        logging.warning(f"No LDRBrachyPlan object not created for {path_to_rt_plan_file} "
                        f"because positions or context is empty")
        return None

    brachy_plan = LDRBrachyPlan(context["RTPlan"], context["RefRtStructUID"],
                                context["RefRtDoseUID"], context["RTPlanDate"], context["RTPlanTime"])
    list_of_sources = []
    for sources in positions.keys():
        source = Sources(context[sources]["SourceIsotopeName"], context[sources]["ReferenceAirKermaRate"],
                         context[sources]["SourceStrengthReferenceDate"],
                         context[sources]["SourceStrengthReferenceTime"], context[sources]["MaterialID"],
                         context[sources]["SourceType"], context[sources]["SourceManufacturer"],
                         context[sources]["ActiveSourceDiameter"], context[sources]["ActiveSourceLength"],
                         positions[sources]["positions"], positions[sources]["orientations"],
                         brachy_plan)
        list_of_sources.append(source)

    brachy_plan.add_sources(list_of_sources)

    return brachy_plan
