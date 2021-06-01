import pydicom
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def generate_3d_image_from_series(path_to_series_folder:str) -> np.ndarray:
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
    pass



plot_whole_series(r"E:\DICOMS\oncoweb\patient4\study0\series4")













