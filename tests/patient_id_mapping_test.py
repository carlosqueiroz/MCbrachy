import unittest
import csv
import os
import logging

from preprocessing_pipeline_components import patient_id_mapping as pat_id

from root import ROOT

test_log_filename = os.path.join(ROOT, "logs", "test_logs")
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, "tests", "test_data")


class TestIsPatientIDMapped(unittest.TestCase):
    def setUp(self):
        patient_id_mapping_test_file_path = os.path.join(data_folder, "patientID_mapping_test.csv")
        with open(patient_id_mapping_test_file_path, 'a', newline='') as csv_file:
            mapping_writer = csv.writer(csv_file, delimiter=";")
            mapping_writer.writerow(["Original PatientID", "New PatientID"])
        pat_id.patient_id_mapping_file_path = patient_id_mapping_test_file_path

    def test_csv_not_created_or_wrong_colomns(self):
        if os.path.exists(pat_id.patient_id_mapping_file_path):
            os.remove(pat_id.patient_id_mapping_file_path)
        mapped, row = pat_id.is_patient_id_mapped("Dummy_PatientId")
        self.assertFalse(mapped)
        self.assertEqual(row, -1)
        with open(pat_id.patient_id_mapping_file_path, 'a', newline='') as csv_file:
            mapping_writer = csv.writer(csv_file, delimiter=";")
            mapping_writer.writerow(["Wrong", "New PatientID"])
        mapped, row = pat_id.is_patient_id_mapped("Dummy_PatientId")
        self.assertFalse(mapped)
        self.assertEqual(row, -1)
        if os.path.exists(pat_id.patient_id_mapping_file_path):
            os.remove(pat_id.patient_id_mapping_file_path)
        with open(pat_id.patient_id_mapping_file_path, 'a', newline='') as csv_file:
            mapping_writer = csv.writer(csv_file, delimiter=";")
            mapping_writer.writerow(["Original PatientID", "Wrong"])
        mapped, row = pat_id.is_patient_id_mapped("Dummy_PatientId")
        self.assertFalse(mapped)
        self.assertEqual(row, -1)

    def test_normal_cases(self):
        mapped, row = pat_id.is_patient_id_mapped("Dummy_PatientId")
        self.assertFalse(mapped)
        self.assertEqual(row, -1)
        with open(pat_id.patient_id_mapping_file_path, 'a', newline='') as csv_file:
            mapping_writer = csv.writer(csv_file, delimiter=";")
            mapping_writer.writerow(["Dummy_PatientId", "New PatientID"])
            mapping_writer.writerow(["Dummy_PatientId2", "Dummy_PatientId3"])
        mapped, row = pat_id.is_patient_id_mapped("Dummy_PatientId")
        self.assertTrue(mapped)
        self.assertEqual(row, 1)
        mapped, row = pat_id.is_patient_id_mapped("Dummy_PatientId3")
        self.assertTrue(mapped)
        self.assertEqual(row, 2)

    def tearDown(self) -> None:
        if os.path.exists(pat_id.patient_id_mapping_file_path):
            os.remove(pat_id.patient_id_mapping_file_path)


class TestMapNewPatientID(unittest.TestCase):
    def setUp(self):
        patient_id_mapping_test_file_path = os.path.join(data_folder, "patientID_mapping_test.csv")
        with open(patient_id_mapping_test_file_path, 'a', newline='') as csv_file:
            mapping_writer = csv.writer(csv_file, delimiter=";")
            mapping_writer.writerow(["Original PatientID", "New PatientID"])
        pat_id.patient_id_mapping_file_path = patient_id_mapping_test_file_path

    def test_csv_not_created(self):
        if os.path.exists(pat_id.patient_id_mapping_file_path):
            os.remove(pat_id.patient_id_mapping_file_path)
        pat_id.map_new_patient_id_with_old_one("NewPatientID", "OldPatientID")

        with open(pat_id.patient_id_mapping_file_path) as csv_file:
            csv_reader_list = list(csv.reader(csv_file, delimiter=";"))
            self.assertEqual(csv_reader_list[0], ["Original PatientID", "New PatientID"])
            self.assertEqual(csv_reader_list[1], ["OldPatientID", "NewPatientID"])

    def test_normal_cases(self):
        pat_id.map_new_patient_id_with_old_one("NewPatientID", "OldPatientID")

        with open(pat_id.patient_id_mapping_file_path) as csv_file:
            csv_reader_list = list(csv.reader(csv_file, delimiter=";"))
            self.assertEqual(csv_reader_list[0], ["Original PatientID", "New PatientID"])
            self.assertEqual(csv_reader_list[1], ["OldPatientID", "NewPatientID"])
            self.assertEqual(2, len(csv_reader_list))

        pat_id.map_new_patient_id_with_old_one("NewPatientID", "OldPatientID")
        with open(pat_id.patient_id_mapping_file_path) as csv_file:
            csv_reader_list = list(csv.reader(csv_file, delimiter=";"))
            self.assertEqual(csv_reader_list[0], ["Original PatientID", "New PatientID"])
            self.assertEqual(csv_reader_list[1], ["OldPatientID", "NewPatientID"])
            self.assertEqual(2, len(csv_reader_list))

    def tearDown(self) -> None:
        if os.path.exists(pat_id.patient_id_mapping_file_path):
            os.remove(pat_id.patient_id_mapping_file_path)


class TestGetIDConversion(unittest.TestCase):
    def setUp(self):
        patient_id_mapping_test_file_path = os.path.join(data_folder, "patientID_mapping_test.csv")
        with open(patient_id_mapping_test_file_path, 'a', newline='') as csv_file:
            mapping_writer = csv.writer(csv_file, delimiter=";")
            mapping_writer.writerow(["Original PatientID", "New PatientID"])
            mapping_writer.writerow(["OLD1", "NEW1"])
            mapping_writer.writerow(["OLD2", "NEW2"])
            mapping_writer.writerow(["OLD3", "NEW3"])
            mapping_writer.writerow(["OLD4", "NEW4"])
        pat_id.patient_id_mapping_file_path = patient_id_mapping_test_file_path

    def test_absent_patientID(self):
        self.assertEqual(None, pat_id.get_patient_id_conversion("OLD102"))
        self.assertEqual(None, pat_id.get_patient_id_conversion("NEW102"))

    def test_normal_cases(self):
        self.assertEqual("NEW1", pat_id.get_patient_id_conversion("OLD1"))
        self.assertEqual("NEW2", pat_id.get_patient_id_conversion("OLD2"))
        self.assertEqual("NEW3", pat_id.get_patient_id_conversion("OLD3"))
        self.assertEqual("NEW4", pat_id.get_patient_id_conversion("OLD4"))
        self.assertEqual("OLD1", pat_id.get_patient_id_conversion("NEW1"))
        self.assertEqual("OLD2", pat_id.get_patient_id_conversion("NEW2"))
        self.assertEqual("OLD3", pat_id.get_patient_id_conversion("NEW3"))
        self.assertEqual("OLD4", pat_id.get_patient_id_conversion("NEW4"))

    def tearDown(self) -> None:
        if os.path.exists(pat_id.patient_id_mapping_file_path):
            os.remove(pat_id.patient_id_mapping_file_path)


if __name__ == '__main__':
    unittest.main()
