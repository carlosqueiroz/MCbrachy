import os
import unittest
from root import ROOT
from extraction_pipeline_components.contour_extraction_as_masks import *

test_log_filename = os.path.join(ROOT, "logs", "test_logs")
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, "tests", "test_data")


class TestExtractContourMaskAndImageTools(unittest.TestCase):
    def test_build_image_references_dict(self):
        path_rt_struct = os.path.join(data_folder, "test_patient", "study", "rt_struct", "RTSTRUCT109.dcm")
        dicom_json = pydicom.dcmread(path_rt_struct).to_json_dict()
        dict_of_uids = build_image_references_dict(dicom_json)
        self.assertEqual(len(dict_of_uids.keys()), 99)
        self.assertEqual("1.2.826.0.1.3680043.10.424.4622819306153995064730756749996437394", dict_of_uids[1])
        self.assertEqual("1.2.826.0.1.3680043.10.424.3647330314384465897480925715125008422", dict_of_uids[99])
        path_rt_struct = os.path.join(data_folder, "RTSTRUCT_no_frame_number.dcm")
        dicom_json = pydicom.dcmread(path_rt_struct).to_json_dict()
        dict_of_uids = build_image_references_dict(dicom_json)
        self.assertEqual(len(dict_of_uids.keys()), 198)
        self.assertEqual("1.3.6.1.4.1.14519.5.2.1.2193.7172.260209224923274040650639981398", dict_of_uids[1])
        self.assertEqual("1.3.6.1.4.1.14519.5.2.1.2193.7172.686245034710838675764102222123", dict_of_uids[198])

    def test_convert_real_coordinates_into_pixel_tuple_coordinates(self):
        test_data = np.asarray([[12.2, 10.5, 11.4], [10.2, 10.0, 11.4]])
        pixel_pos = convert_real_coordinates_into_pixel_tuple_coordinates(test_data, (0.2, 0.1, 0.2), [10., 10., 10.],
                                                                          [1, 0, 0, 0, 1, 0])
        self.assertEqual([(11, 5), (1, 0)], pixel_pos)


class TestExtractContourContextInfo(unittest.TestCase):
    def test_case_1(self):
        path_rt_struct = os.path.join(data_folder, "test_patient", "study", "rt_struct", "RTSTRUCT109.dcm")
        dicom_json = pydicom.dcmread(path_rt_struct).to_json_dict()
        contour_context = extract_contour_context_info(dicom_json)
        self.assertEqual(len(contour_context.keys()), 9)

    def test_case_2(self):
        path_rt_struct = os.path.join(data_folder, "RTSTRUCT_no_frame_number.dcm")
        dicom_json = pydicom.dcmread(path_rt_struct).to_json_dict()
        contour_context = extract_contour_context_info(dicom_json)
        self.assertEqual(45, len(contour_context.keys()))


class TestExtractMasksForEachOrgansForEachSlices(unittest.TestCase):
    def test_normal_case(self):
        path_rt_struct = os.path.join(data_folder, "test_patient", "study", "rt_struct", "RTSTRUCT109.dcm")
        path_to_study = os.path.join(data_folder, "test_patient", "study")
        structures = extract_masks_for_each_organs_for_each_slices(path_rt_struct, path_to_study)
        self.assertEqual(structures.rt_struct_uid, "1.2.826.0.1.3680043.10.424.6377455315485968017200746515229809227")
        self.assertEqual(structures.image_shape, (99, 512, 512))
        self.assertEqual(structures.study_folder, path_to_study)
        self.assertEqual(structures.list_roi_observation_labels(), ['prostate', 'uretre', 'vessie', 'rectum',
                                                                    'Bladder Neck'])
        self.assertEqual(structures.list_roi_names(), ['prostate', 'uretre', 'vessie', 'rectum',
                                                       'Bladder Neck'])
        self.assertEqual(len(structures.list_of_masks), 5)
        self.assertEqual(len(structures.list_of_masks[0].list_mask_slices), 13)
        self.assertEqual(structures.list_of_masks[0].list_slice_numbers(), [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
                                                                            59, 60])

    def test_no_image_case(self):
        path_rt_struct = os.path.join(data_folder, "RTSTRUCT_no_frame_number.dcm")
        path_to_study = os.path.join(data_folder)
        structures = extract_masks_for_each_organs_for_each_slices(path_rt_struct, path_to_study)
        self.assertEqual(structures, None)


if __name__ == '__main__':
    unittest.main()
