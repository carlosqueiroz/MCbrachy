from dicompylercore import dicomparser
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import os
import pydicom
from typing import List

path = r"E:\DICOMS\VS-SEG-001\09-04-1994-Avanto RoutineImage Guidance-88886\94436\1-1.dcm"
dp = dicomparser.DicomParser(path)

list_struc = dp.GetStructureCoordinates(1)['-35.830'][0]["data"]


def convert_list_of_real_coordinates_into_slice_pixel_coordinates(list_x_y_z_coord: List[List[str]],
                                                                  x_y_spacing, x_y_z_origin, x_y_z_rotation_vectors):
    x_spacing, y_spacing = float(x_y_spacing[0]), float(x_y_spacing[1])
    origin_x, origin_y, _ = x_y_z_origin
    coord = np.asarray(list_x_y_z_coord, dtype=np.float64)
    pixel_coords = [(np.ceil((x - origin_x) * (x_y_z_rotation_vectors[0] + x_y_z_rotation_vectors[3]) / x_spacing),
                     np.ceil(
                         (y - origin_y) * (x_y_z_rotation_vectors[1] + x_y_z_rotation_vectors[4]) / y_spacing))
                    for x, y, _ in coord]

    return pixel_coords


def extract_positionning_informations(path_to_dicom_image_asociated_to_the_frame_reference):
    dicom = pydicom.dcmread(path_to_dicom_image_asociated_to_the_frame_reference)
    img_arr = dicom.pixel_array
    img_shape = img_arr.shape
    x_y_spacing = dicom.PixelSpacing[0], dicom.PixelSpacing[1]
    x_y_z_origin = dicom.ImagePositionPatient
    x_y_z_rotation_vectors = dicom.ImageOrientationPatient

    return img_shape, x_y_spacing, x_y_z_origin, x_y_z_rotation_vectors


def produce_mask_from_contour_coord(coord: list, img_shape):
    img = Image.new(mode='L', size=img_shape, color=0)
    ImageDraw.Draw(img).polygon(xy=coord, outline=0, fill=1)
    mask = np.array(img).astype(bool)

    return mask


# y, x is how it's mapped
img_shape, x_y_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
    r"E:\DICOMS\VS-SEG-001\09-04-1994-Avanto RoutineImage Guidance-88886\4.000000-t2ci3dtra1.5mmv1-90998\1-01.dcm")

coord = convert_list_of_real_coordinates_into_slice_pixel_coordinates(list_struc,
                                                                      x_y_spacing,
                                                                      x_y_z_origin,
                                                                      x_y_z_rotation_vectors)

mask = produce_mask_from_contour_coord(coord, img_shape)
print(mask)
pixel_data = 0
for files in os.listdir(
        r"E:\DICOMS\VS-SEG-001\09-04-1994-Avanto RoutineImage Guidance-88886\4.000000-t2ci3dtra1.5mmv1-90998"):
    file_path = os.path.join(
        r"E:\DICOMS\VS-SEG-001\09-04-1994-Avanto RoutineImage Guidance-88886\4.000000-t2ci3dtra1.5mmv1-90998", files)
    open_dicom = pydicom.dcmread(file_path)
    if "1.3.6.1.4.1.14519.5.2.1.44295176855626357755903674408888314327" == open_dicom.SOPInstanceUID:
        pixel_data = open_dicom.pixel_array
        break

plt.imshow(pixel_data)
plt.show()
plt.imshow(pixel_data)
plt.imshow(mask, interpolation='none', alpha=0.7)
plt.show()
