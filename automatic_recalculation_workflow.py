import os
import sys, getopt
import subprocess
from generate_simulation_input_files.generate_simulation_input_files import generate_whole_topas_input_file
from root import ROOT
from dicom_rt_context_extractor.utils.dicom_folder_structurer import restructure_dicom_folder, destructure_folder
from dicom_rt_context_extractor.utils.search_instance_and_convert_coord_in_pixel import find_instance_in_folder, \
    find_modality_in_folder
from dicom_rt_context_extractor.sources_information_extraction import extract_all_sources_informations
from mcdose2dicom.link_to_existing_dicom import adapt_rt_dose_to_existing_rt_dose_grid, add_reference_in_rt_plan
from mcdose2dicom.adding_dvh import generate_and_add_all_dvh_to_dicom
from mcdose2dicom.create_rt_dose_from_scratch import add_data_element_to_dicom
from mcdose2dicom.dicom_tags.rt_dose_tags import DoseUnitsAttribute, DoseTypeAttribute, DoseSummationTypeAttribute


def get_aguments(argv):
    restructuring = False
    recalculation_algorithm = "topas"
    segmenting_calcification = False
    organ_contours_to_use = []
    number_of_particles = 10000

    try:
        opts, args = getopt.getopt(argv, "i:o:a:r:s:p:")
    except getopt.GetoptError:
        print('automatic_recalculation_workflow.py -i <inputfolder> -o <organs_to_use> -a <reacalculation_method> -r '
              '<restructure> -s <segmenting_calcifications>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            if os.path.exists(arg):
                patient_directory = arg
        elif opt == '-o':
            organ_contours_to_use.append(arg)
        elif opt == '-a':
            if arg not in ["topas", "egs_brachy"]:
                print(
                    'automatic_recalculation_workflow.py -i <inputfolder> -o <organs_to_use> -a '
                    '<reacalculation_method> -r '
                    '<restructure> -s <segmenting_calcifications>')
                sys.exit()
            recalculation_algorithm = arg
        elif opt == "-r":
            if arg == "True":
                restructuring = True
            elif arg == "False":
                restructuring = False
            else:
                print(
                    'automatic_recalculation_workflow.py -i <inputfolder> -o <organs_to_use> -a '
                    '<reacalculation_method> -r '
                    '<restructure> -s <segmenting_calcifications>')
                sys.exit()

        elif opt == "-s":
            if arg == "True":
                segmenting_calcification = True
            elif arg == "False":
                segmenting_calcification = False
            else:
                print(
                    'automatic_recalculation_workflow.py -i <inputfolder> -o <organs_to_use> -a '
                    '<reacalculation_method> -r '
                    '<restructure> -s <segmenting_calcifications>')
                sys.exit()

        elif opt == "-p":
            number_of_particles = int(arg)

        else:
            print('automatic_recalculation_workflow.py -i <inputfolder> -a <algorithm> -r <restructure>')
            sys.exit()

    return organ_contours_to_use, recalculation_algorithm, restructuring, segmenting_calcification, number_of_particles


if __name__ == "__main__":
    ORGANS_TO_USE, RECALCULATION_ALGORITHM, RESTRUCTURING_FOLDERS, \
    SEGMENTING_CALCIFICATIONS, NUMBER_OF_PARTICLES = get_aguments(sys.argv[1:-2])
    PATIENTS_DIRECTORY = sys.argv[-2]
    OUTPUT_PATH = sys.argv[-1]

    for patient in os.listdir(PATIENTS_DIRECTORY):
        patient_folder_path = os.path.join(PATIENTS_DIRECTORY, patient)
        if RESTRUCTURING_FOLDERS:
            restructure_dicom_folder(patient_folder_path, patient_folder_path)

        for studies in os.listdir(patient_folder_path):
            study_path = os.path.join(patient_folder_path, studies)

            # Lets find and extract the rt plan first
            rt_plan_path = find_modality_in_folder("RTPLAN", study_path)
            plan = extract_all_sources_informations(rt_plan_path)
            plan.extract_structures(study_path)
            plan.extract_dosimetry(study_path)
            struct = plan.get_structures()
            if SEGMENTING_CALCIFICATIONS:
                struct.add_mask_from_3d_array(plan.segmenting_calcification(10, 2.236, study_path),
                                              roi_name="calcification",
                                              observation_label="masking souces with cylindrical masks with "
                                                                "thresholding",
                                              segmentation_method=1, add_to_original_rt_struct_file=True,
                                              saving_path=os.path.join(OUTPUT_PATH,
                                                                       f"updated_{patient}_{studies}_RTSTRUCT.dcm"))

            if RECALCULATION_ALGORITHM == "egs_brachy":
                # struct.generate_egs_phant_file_from_structures()
                # plan.generate_transformation_files()
                pass

            elif RECALCULATION_ALGORITHM == "topas":
                index_saving_path = os.path.join(ROOT, "simulation_files",
                                                 f"mapping_{patient}_{studies}.bin")
                input_saving_path = os.path.join(ROOT, "simulation_files",
                                                 f"input_{patient}_{studies}.txt")
                output_saving_path = os.path.join(OUTPUT_PATH, f"dose_{patient}_{studies}")
                try:
                    generate_whole_topas_input_file(plan, NUMBER_OF_PARTICLES, ORGANS_TO_USE, output_saving_path,
                                                    input_saving_path, index_saving_path,
                                                    add="i:Ts/NumberOfThreads = -2")
                    bash_command = f"/topas/topas/bin/topas {input_saving_path}"
                    os.chmod(input_saving_path, 0o777)
                    os.chmod(index_saving_path, 0o777)
                    simulation = subprocess.run(bash_command.split())
                    path_to_rt_dose = find_instance_in_folder(plan.rt_dose_uid, study_path)
                    adapt_rt_dose_to_existing_rt_dose_grid(output_saving_path + ".dcm", path_to_rt_dose)
                    add_data_element_to_dicom(DoseUnitsAttribute("GY"), output_saving_path + ".dcm")
                    add_data_element_to_dicom(DoseTypeAttribute("PHYSICAL"), output_saving_path + ".dcm")
                    add_data_element_to_dicom(DoseTypeAttribute("PHYSICAL"), output_saving_path + ".dcm")
                    add_data_element_to_dicom(DoseSummationTypeAttribute("PLAN"), output_saving_path + ".dcm")
                    add_reference_in_rt_plan(rt_plan_path,
                                             output_saving_path + ".dcm", os.path.join(OUTPUT_PATH,
                                                                                       f"updated_{patient}_{studies}_RTPLAN.dcm"))

                    path_to_rt_struct = find_instance_in_folder(plan.rt_struct_uid, study_path)
                    generate_and_add_all_dvh_to_dicom(output_saving_path + ".dcm", os.path.join(OUTPUT_PATH,
                                                                                                f"updated_{patient}_{studies}_RTSTRUCT.dcm"),
                                                      output_saving_path + ".dcm", "DVH generated by dicompyler",
                                                      dose_scaling_factor=1.0, dose_type="PHYSICAL",
                                                      contribution_type="INCLUDE", prescription_dose=144)
                except NotImplementedError:
                    continue

        if RESTRUCTURING_FOLDERS:
            destructure_folder(patient_folder_path)
