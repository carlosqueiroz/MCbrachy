import pydicom
import numpy as np
import os
import logging
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def generate_3d_image_from_series(path_to_series_folder: str) -> np.ndarray:
    """
    This method produces a single 3d ndarray from all the instances containing an image in a series.
    For it to work, instance numbers must be from 1 to the last instance number without any missing slice.

    :param path_to_series_folder: path to the series folder
    :return: the 3d array or np.zeros(1) in abnormal cases
    """

    path_to_first_instance_dicom = os.path.join(path_to_series_folder, os.listdir(path_to_series_folder)[0])
    try:
        slice_shape = pydicom.dcmread(path_to_first_instance_dicom).pixel_array.shape
        empty_3d_array = np.zeros((*slice_shape, len(os.listdir(path_to_series_folder))), dtype=np.float32)
        for files in os.listdir(path_to_series_folder):
            path_to_dicom = os.path.join(path_to_series_folder, files)
            open_dicom = pydicom.dcmread(path_to_dicom)
            if open_dicom.Modality not in ["CT", "MR", "RTIMAGE", "CR", "PT", "US"]:
                raise AttributeError

            instance_number = int(open_dicom.InstanceNumber)
            empty_3d_array[:, :, instance_number - 1] = open_dicom.pixel_array

        return empty_3d_array

    except (AttributeError, IndexError):
        logging.warning(f"Series {path_to_series_folder} does not contain images or there "
                        f"is an other modality among the images.")

        return np.zeros(1)


def plot_whole_series(path_to_series_folder: str) -> bool:
    """
    Using the generate_3d_image_from_series to produce the 3d image arry,
    this method plots the 3d image slices by sclices. A slider allows the user to
    freely look at any slice.

    :param path_to_series_folder: path to the series folder
    :return: whether or not there was something to plot.
    """
    try:
        values = generate_3d_image_from_series(path_to_series_folder)
        if values.shape == np.zeros(1).shape:
            logging.warning(f"Series {path_to_series_folder} had nothing to plot for verification.")
            return False

        max_slice = values.shape[2] - 1

        plt.subplots_adjust(bottom=0.25)
        dicom_3d_image = plt.imshow(values[:, :, int(max_slice/2)])
        axslice = plt.axes([0.20, 0.15, 0.65, 0.02], facecolor='lightgoldenrodyellow')
        slice_index = Slider(axslice, 'Slice', 0, max_slice, valinit=int(max_slice/2), valstep=1)

        def update(val):
            slice_value = slice_index.val
            dicom_3d_image.set_data(values[:, :, slice_value])
            plt.draw()

        slice_index.on_changed(update)
        plt.show()

        return True

    except:
        logging.warning(f"Something went wrong while plotting series {path_to_series_folder}.")
        return False


def manual_selection_of_calcification(path_to_series_folder: str) -> bool:
    """
    This method will show the 3d image in the folder. After the user has
    searched for calcification and closed the plot, the command prompt will ask the user
    to enter whether or not there was calcification in the image.

    :param path_to_series_folder:  path to the series folder
    :return: Whether or no there was calcification (True or False
    """
    had_something_to_plot = plot_whole_series(path_to_series_folder)
    if not had_something_to_plot:
        logging.warning(f"No manual selection for series {path_to_series_folder} because there was no image to show"
                        f"False is automatically returned in these cases.")
        return False

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
    This method will inspect successive series folder in the study in search
    for calcification. For each series containing images, the 3d image will be
    plotted, the user will verify if there is calcification. Unless calcification
    is found, this method will keep looking into the other series until there are none left.

    :param path_to_study_folder: path to the study folder
    :return: Whether or not there was calcification in at least one series.
    """
    image_found = False
    for folders in os.listdir(path_to_study_folder):
        series_folder = os.path.join(path_to_study_folder, folders)
        first_instance_path = os.path.join(series_folder, os.listdir(series_folder)[0])
        if pydicom.dcmread(first_instance_path).Modality in ["CT", "MR", "RTIMAGE", "CR", "PT", "US"]:
            image_found = True
            presence_of_calcification = manual_selection_of_calcification(series_folder)

            if presence_of_calcification:
                return True

    if not image_found:
        logging.warning(f"No images found in study: {path_to_study_folder}")

    return False
