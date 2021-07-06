import logging

import pydicom


# will need LDR rt plan
def extract_sources_positions(path_to_rt_plan_file):
    return {}


def extract_sources_context_information(path_to_rt_plan_file):
    open_dicom = pydicom.dcmread(path_to_rt_plan_file)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()
            source_sequence = json_version_dicom["300A0210"]["Value"]
            sources_dict = {"RTPlanDate": json_version_dicom["300A0006"],
                            "RTPlanTime": json_version_dicom["300A0007"]}

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
        logging.warning(f"")

        return {}


def extract_all_sources_informations(path_to_rt_plan_file):
    context = extract_sources_context_information(path_to_rt_plan_file)
    positions = extract_sources_positions(path_to_rt_plan_file)

    for sources in positions.keys():
        context[sources].update(positions[sources])

    return context

