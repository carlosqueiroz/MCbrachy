import logging
import unittest
from extraction_pipeline_components.mask_structure_classes import *
from extraction_pipeline_components.search_instance_and_convert_coord_in_pixel import extract_positionning_informations
from root import ROOT

test_log_filename = os.path.join(ROOT, r'logs\test_logs')
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, r'tests\test_data')


class TestStructures(unittest.TestCase):
    def test_add_masks_one(self):
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)
        structure = Structures((100, img_shape_2d[0], img_shape_2d[1]),
                               x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors, [], "study_folder")
        structure.add_masks(Mask("roi_name", "observation_label", structure, []))
        self.assertEqual(1, len(structure.list_of_masks))

    def test_add_masks_many(self):
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)
        structure = Structures((100, img_shape_2d[0], img_shape_2d[1]),
                               x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors, [], "study_folder")
        structure.add_masks([Mask("roi_name", "observation_label", structure, []),
                             Mask("roi_name", "observation_label", structure, []),
                             Mask("roi_name", "observation_label", structure, [])])
        self.assertEqual(3, len(structure.list_of_masks))


class TestMask(unittest.TestCase):
    def test_add_slices_one(self):
        self.assertEqual(False, False)
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)
        structure = Structures((100, img_shape_2d[0], img_shape_2d[1]),
                               x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors, [], "study_folder")
        mask = Mask("roi_name", "observation_label", structure, [])
        mask.add_slices(SliceMask(np.asarray([1, 3, 3]), "uid", 0, mask))
        self.assertEqual(1, len(mask.list_mask_slices))

    def test_add_slices_many(self):
        self.assertEqual(False, False)
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)
        structure = Structures((100, img_shape_2d[0], img_shape_2d[1]),
                               x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors, [], "study_folder")
        mask = Mask("roi_name", "observation_label", structure, [])
        mask.add_slices([SliceMask(np.asarray([1, 3, 3]), "uid", 0, mask),
                        SliceMask(np.asarray([1, 3, 3]), "uid", 0, mask),
                        SliceMask(np.asarray([1, 3, 3]), "uid", 0, mask)])
        self.assertEqual(3, len(mask.list_mask_slices))


class TestSliceMask(unittest.TestCase):
    def test_get_slice_mask_with_image(self):
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)
        study_folder = os.path.join(data_folder, "fictional_study")
        uid = "1.3.6.1.4.1.14519.5.2.1.226742563510968359814545353392980263364"
        structure = Structures((100, img_shape_2d[0], img_shape_2d[1]),
                               x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors, [], study_folder)
        mask = Mask("roi_name", "observation_label", structure, [])
        slice = SliceMask(np.asarray([1, 3, 3]), uid, 0, mask)
        image, mask = slice.get_slice_mask_with_image()
        self.assertFalse((mask - np.asarray([1, 3, 3])).any())
        dicom = pydicom.dcmread(path_to_image)
        self.assertFalse((dicom.pixel_array - image).any())


class TestAllClassesTogether(unittest.TestCase):
    def test_get_specific_mask(self):
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)
        structure = Structures((100, img_shape_2d[0], img_shape_2d[1]),
                               x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors, [], "study_folder")
        mask1 = Mask("roi_name1", "observation_label1", structure, [])
        mask1 = Mask("roi_name1", "observation_label1", structure, [])

    def test_list_roi_names(self):
        self.assertEqual(False, False)

    def test_list_roi_observation_labels(self):
        self.assertEqual(False, False)

    def test_list_slice_numbers(self):
        self.assertEqual(False, False)

    def test_get_specific_slice(self):
        self.assertEqual(False, False)


if __name__ == '__main__':
    unittest.main()
