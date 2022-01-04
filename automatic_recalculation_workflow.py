import os
import sys, getopt
import subprocess
from root import ROOT
from extraction_pipeline_components.utils.dicom_folder_structurer import restructure_dicom_folder, destructure_folder
from extraction_pipeline_components.utils.search_instance_and_convert_coord_in_pixel import find_instance_in_folder, \
    find_modality_in_folder
from extraction_pipeline_components.sources_information_extraction import extract_all_sources_informations


def get_aguments(argv):
    patient_directory = None
    restructuring = False
    recalculation_algorithm = "topas"
    segmenting_calcification = False
    organ_contours_to_use = []

    try:
        opts, args = getopt.getopt(argv, "i:o:a:r:s:")
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

        else:
            print('automatic_recalculation_workflow.py -i <inputfolder> -a <algorithm> -r <restructure>')
            sys.exit()

    return patient_directory, organ_contours_to_use, recalculation_algorithm, restructuring, segmenting_calcification


if __name__ == "__main__":
    PATIENTS_DIRECTORY, ORGANS_TO_USE, RECALCULATION_ALGORITHM, RESTRUCTURING_FOLDERS, \
    SEGMENTING_CALCIFICATIONS = get_aguments(sys.argv[1:])
    print(PATIENTS_DIRECTORY, ORGANS_TO_USE, RECALCULATION_ALGORITHM, RESTRUCTURING_FOLDERS, \
    SEGMENTING_CALCIFICATIONS)
    if PATIENTS_DIRECTORY is None:
        print('automatic_recalculation_workflow.py -i <inputfolder> -a <algorithm> -r <restructure>')
        sys.exit()

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
                                              segmentation_method=1, add_to_original_rt_struct_file=True)
            if RECALCULATION_ALGORITHM == "egs_brachy":
                # struct.generate_egs_phant_file_from_structures()
                # plan.generate_transformation_files()
                pass

            elif RECALCULATION_ALGORITHM == "topas":
                photon_per_seed = 100
                index_saving_path = os.path.join(ROOT, "simulation_files/3d_index_mapping",
                                                 f"mapping_{patient}_{studies}")
                input_saving_path = os.path.join(ROOT, "simulation_files/topas_simulation_files",
                                                 f"input_{patient}_{studies}")
                output_saving_path = os.path.join(ROOT, "simulation_files/topas_simulation_files",
                                                  f"dose_{patient}_{studies}")
                plan.generate_whole_topas_input_file(100, ORGANS_TO_USE, output_saving_path, input_saving_path,
                                                     index_saving_path, add="i:Ts/NumberOfThreads = 7")
                simulation = subprocess.Popen(f"topas {input_saving_path}")

        if RESTRUCTURING_FOLDERS:
            destructure_folder(patient_folder_path)
