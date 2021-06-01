import pydicom
import numpy as np
import os
import logging
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def generate_3d_image_from_series(path_to_series_folder: str) -> np.ndarray:
    """

    :param path_to_series_folder:
    :return:
    """
    path_to_first_instance_dicom = os.path.join(path_to_series_folder, os.listdir(path_to_series_folder)[0])
    slice_shape = pydicom.dcmread(path_to_first_instance_dicom).pixel_array.shape
    empty_3d_array = np.zeros((*slice_shape, len(os.listdir(path_to_series_folder))), dtype=np.float32)
    for files in os.listdir(path_to_series_folder):
        path_to_dicom = os.path.join(path_to_series_folder, files)
        open_dicom = pydicom.dcmread(path_to_dicom)
        instance_number = int(open_dicom.InstanceNumber)
        empty_3d_array[:, :, instance_number - 1] = open_dicom.pixel_array

    return empty_3d_array


def plot_whole_series(path_to_series_folder: str):
    """

    :param path_to_series_folder:
    :return:
    """
    values = generate_3d_image_from_series(path_to_series_folder)
    max_slice = values.shape[2] - 1

    plt.subplots_adjust(bottom=0.25)
    dicom_3d_image = plt.imshow(values[:, :, int(max_slice/2)])
    axslice = plt.axes([0.20, 0.15, 0.65, 0.02], facecolor='lightgoldenrodyellow')
    slice_index = Slider(axslice, 'Slice', 0, max_slice, valinit=int(max_slice/2), valstep=1)

    def update(val):
        slice = slice_index.val
        dicom_3d_image.set_data(values[:, :, slice])
        plt.draw()

    slice_index.on_changed(update)
    plt.show()


def manual_selection_of_calcification(path_to_series_folder):
    """

    :param path_to_series_folder:
    :return:
    """
    plot_whole_series(path_to_series_folder)
    is_answer_valid = True
    answer = None
    while is_answer_valid:
        print('Was there any prostate calcification in the image?')
        answer = get_input("(Yes or No):")
        if answer == "Yes" or answer == "No":
            is_answer_valid = False

    if answer == "Yes":
        return True

    if answer != "No":
        logging.warning(f"Something unexpected occured in the manual selection for series {path_to_series_folder}."
                        f"False is automatically returned in these cases.")
    return False


def get_input(text):
    return input(text)


def is_there_prostate_calcification_in_study(path_to_study_folder: str) -> bool:
    """

    :param path_to_study_folder:
    :return:
    """
    for folders in os.listdir(path_to_study_folder):
        series_folder = os.path.join(path_to_study_folder, folders)
        first_instance_path = os.path.join(series_folder, os.listdir(series_folder)[0])
        if pydicom.dcmread(first_instance_path).Modality in ["CT", "MR", "RTIMAGE", "CR", "PT", "US"]:
            presence_of_calcification = manual_selection_of_calcification(series_folder)
            if presence_of_calcification:
                return True

    return False
