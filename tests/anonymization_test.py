import shutil
import unittest
import os
import logging
import pydicom
from preprocessing_pipeline_components import anonymization as anonym
from dicom_anonymiseur.util import hash_value
from root import ROOT

test_log_filename = os.path.join(ROOT, r'logs\test_logs')
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, r'tests\test_data')


class TestAnonymizeSingleDICOM(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.anonymized_data_dirname = "dummy_str"

    def test_new_patient_id(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        initial_dicom = pydicom.dcmread(data_path)
        initial_patient_id = initial_dicom.PatientID
        dicom_modality = pydicom.dcmread(data_path).Modality
        self.anonymized_data_dirname = os.path.join(data_folder, "new_patient_ID")
        anonym.anonymize_single_DICOM(data_path, data_folder, "new_patient_ID")
        anonymized_data_path = os.path.join(data_folder, "new_patient_ID", "study", "series", f"{dicom_modality}0.dcm")
        anonymized_dicom = pydicom.dcmread(anonymized_data_path)
        anonymized_patientID = anonymized_dicom.PatientID

        self.assertNotEqual(initial_patient_id, anonymized_patientID)
        self.assertEqual("new_patient_ID", anonymized_patientID)

    def test_new_institution_name(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        dicom_modality = pydicom.dcmread(data_path).Modality
        initial_patient_id = pydicom.dcmread(data_path).PatientID
        try:
            initial_institution_name = pydicom.dcmread(data_path).InstitutionName
        except AttributeError:
            initial_institution_name = None

        self.anonymized_data_dirname = os.path.join(data_folder, "new_patient_ID")
        anonym.anonymize_single_DICOM(data_path, data_folder, "new_patient_ID")
        anonymized_data_path = os.path.join(data_folder, "new_patient_ID", "study", "series", f"{dicom_modality}0.dcm")
        anonymized_dicom = pydicom.dcmread(anonymized_data_path)
        anonymized_institution_name = anonymized_dicom.InstitutionName

        self.assertNotEqual(initial_institution_name, anonymized_institution_name)
        self.assertEqual(hash_value(initial_patient_id[:5]), anonymized_institution_name)

    def test_if_original_DICOM_unchanged(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        initial_patient_id = pydicom.dcmread(data_path).PatientID
        try:
            initial_institution_name = pydicom.dcmread(data_path).InstitutionName
        except AttributeError:
            initial_institution_name = None
        self.anonymized_data_dirname = os.path.join(data_folder, "new_patient_ID")
        anonym.anonymize_single_DICOM(data_path, data_folder, "new_patient_ID")
        post_patient_id = pydicom.dcmread(data_path).PatientID
        try:
            post_institution_name = pydicom.dcmread(data_path).InstitutionName
        except AttributeError:
            post_institution_name = None

        self.assertEqual(initial_patient_id, post_patient_id)
        self.assertEqual(initial_institution_name, post_institution_name)

    def test_anonymization(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        initial_dicom = pydicom.dcmread(data_path)
        initial_instance_uid = initial_dicom.SOPInstanceUID
        initial_series_uid = initial_dicom.SeriesInstanceUID
        dicom_modality = pydicom.dcmread(data_path).Modality
        self.anonymized_data_dirname = os.path.join(data_folder, "new_patient_ID")
        anonym.anonymize_single_DICOM(data_path, data_folder, "new_patient_ID")
        anonymized_data_path = os.path.join(data_folder, "new_patient_ID", "study", "series", f"{dicom_modality}0.dcm")
        anonymized_dicom = pydicom.dcmread(anonymized_data_path)
        anonymized_instance_uid = anonymized_dicom.SOPInstanceUID
        anonymized_series_uid = anonymized_dicom.SeriesInstanceUID

        self.assertNotEqual(initial_series_uid, anonymized_series_uid)
        self.assertNotEqual(initial_instance_uid, anonymized_instance_uid)
        self.assertEqual(anonymized_series_uid, "1.2.826.0.1.3680043.10.424.7023867216555737430473303914711639611")
        self.assertEqual(anonymized_instance_uid, "1.2.826.0.1.3680043.10.424.1297314044383254387606992106650282561")

    def tearDown(self) -> None:
        if os.path.exists(self.anonymized_data_dirname):
            shutil.rmtree(self.anonymized_data_dirname)


class TestAnonymizeWholeFolders(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.anonymized_data_dirname = "dummy_str"

    def test_anonymization_whole_series(self):
        series_folder = os.path.join(data_folder, 'VS-SEG-001', "study", "01992")
        data_path = os.path.join(series_folder, "1-1.dcm")
        initial_dicom = pydicom.dcmread(data_path)
        initial_instance_uid = initial_dicom.SOPInstanceUID
        initial_series_uid = initial_dicom.SeriesInstanceUID
        dicom_modality = pydicom.dcmread(data_path).Modality
        self.anonymized_data_dirname = os.path.join(data_folder, "new_patient_ID")
        anonym.anonymize_whole_series(series_folder, data_folder, "new_patient_ID")
        anonymized_data_path = os.path.join(data_folder, "new_patient_ID", "study", "series", f"{dicom_modality}0.dcm")
        anonymized_dicom = pydicom.dcmread(anonymized_data_path)
        anonymized_instance_uid = anonymized_dicom.SOPInstanceUID
        anonymized_series_uid = anonymized_dicom.SeriesInstanceUID

        new_patient_folder = os.path.join(data_folder, "new_patient_ID")
        new_study_folder = os.path.join(new_patient_folder, "study")
        new_series_folder = os.path.join(new_study_folder, "series")
        self.assertTrue(os.path.exists(new_patient_folder))
        self.assertTrue(os.path.exists(new_study_folder))
        self.assertTrue(os.path.exists(new_series_folder))

        self.assertNotEqual(initial_series_uid, anonymized_series_uid)
        self.assertNotEqual(initial_instance_uid, anonymized_instance_uid)
        self.assertEqual(anonymized_series_uid, "1.2.826.0.1.3680043.10.424.7023867216555737430473303914711639611")
        self.assertEqual(anonymized_instance_uid, "1.2.826.0.1.3680043.10.424.1297314044383254387606992106650282561")

    def test_anonymization_whole_study(self):
        study_folder = os.path.join(data_folder, 'VS-SEG-001', "study")
        data_path = os.path.join(study_folder, '01992', "1-1.dcm")
        initial_dicom = pydicom.dcmread(data_path)
        initial_instance_uid = initial_dicom.SOPInstanceUID
        initial_series_uid = initial_dicom.SeriesInstanceUID
        dicom_modality = pydicom.dcmread(data_path).Modality
        self.anonymized_data_dirname = os.path.join(data_folder, "new_patient_ID")
        anonym.anonymize_whole_study(study_folder, data_folder, "new_patient_ID")
        anonymized_data_path = os.path.join(data_folder, "new_patient_ID", "study", "series0", f"{dicom_modality}0.dcm")
        anonymized_dicom = pydicom.dcmread(anonymized_data_path)
        anonymized_instance_uid = anonymized_dicom.SOPInstanceUID
        anonymized_series_uid = anonymized_dicom.SeriesInstanceUID

        new_patient_folder = os.path.join(data_folder, "new_patient_ID")
        new_study_folder = os.path.join(new_patient_folder, "study")
        new_series_folder = os.path.join(new_study_folder, "series0")
        self.assertTrue(os.path.exists(new_patient_folder))
        self.assertTrue(os.path.exists(new_study_folder))
        self.assertTrue(os.path.exists(new_series_folder))

        self.assertNotEqual(initial_series_uid, anonymized_series_uid)
        self.assertNotEqual(initial_instance_uid, anonymized_instance_uid)
        self.assertEqual(anonymized_series_uid, "1.2.826.0.1.3680043.10.424.7023867216555737430473303914711639611")
        self.assertEqual(anonymized_instance_uid, "1.2.826.0.1.3680043.10.424.1297314044383254387606992106650282561")

    def test_anonymization_whole_patient(self):
        patient_folder = os.path.join(data_folder, 'VS-SEG-001')
        data_path = os.path.join(patient_folder, "study", '01992', "1-1.dcm")
        initial_dicom = pydicom.dcmread(data_path)
        initial_instance_uid = initial_dicom.SOPInstanceUID
        initial_series_uid = initial_dicom.SeriesInstanceUID
        dicom_modality = pydicom.dcmread(data_path).Modality
        self.anonymized_data_dirname = os.path.join(data_folder, "new_patient_ID")
        anonym.anonymize_whole_patient(patient_folder, data_folder, "new_patient_ID")
        anonymized_data_path = os.path.join(data_folder, "new_patient_ID", "study0", "series0",
                                            f"{dicom_modality}0.dcm")
        anonymized_dicom = pydicom.dcmread(anonymized_data_path)
        anonymized_instance_uid = anonymized_dicom.SOPInstanceUID
        anonymized_series_uid = anonymized_dicom.SeriesInstanceUID

        new_patient_folder = os.path.join(data_folder, "new_patient_ID")
        new_study_folder = os.path.join(new_patient_folder, "study0")
        new_series_folder = os.path.join(new_study_folder, "series0")
        self.assertTrue(os.path.exists(new_patient_folder))
        self.assertTrue(os.path.exists(new_study_folder))
        self.assertTrue(os.path.exists(new_series_folder))

        self.assertNotEqual(initial_series_uid, anonymized_series_uid)
        self.assertNotEqual(initial_instance_uid, anonymized_instance_uid)
        self.assertEqual(anonymized_series_uid, "1.2.826.0.1.3680043.10.424.7023867216555737430473303914711639611")
        self.assertEqual(anonymized_instance_uid, "1.2.826.0.1.3680043.10.424.1297314044383254387606992106650282561")

    def tearDown(self) -> None:
        if os.path.exists(self.anonymized_data_dirname):
            shutil.rmtree(self.anonymized_data_dirname)


if __name__ == '__main__':
    unittest.main()
