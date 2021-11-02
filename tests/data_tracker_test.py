import unittest
import os
import logging
import json
from preprocessing_pipeline_components import data_tracker
from root import ROOT

test_log_filename = os.path.join(ROOT, "logs", "test_logs")
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, "tests", "test_data")


class TestAddExpressionToTreatmentVocab(unittest.TestCase):
    def setUp(self):
        test_anonymization_uids_met_path = os.path.join(data_folder, "anonymization_uids_met_path.json")
        anonymization_uids_met_file = open(test_anonymization_uids_met_path, "w")
        json.dump([], anonymization_uids_met_file)
        anonymization_uids_met_file.close()
        data_tracker.anonymized_uids_met_path = test_anonymization_uids_met_path

    def test_dicom_has_already_been_looked_into(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        verification = data_tracker.dicom_has_already_been_looked_into(data_path)
        self.assertFalse(verification)
        test_anonymization_uids_met_path = os.path.join(data_folder, "anonymization_uids_met_path.json")
        anonymization_uids_met_file = open(test_anonymization_uids_met_path, "w")
        json.dump(["1.2.826.0.1.3680043.10.424.1297314044383254387606992106650282561"], anonymization_uids_met_file)
        anonymization_uids_met_file.close()
        verification = data_tracker.dicom_has_already_been_looked_into(data_path)
        self.assertTrue(verification)
        anonymization_uids_met_file = open(test_anonymization_uids_met_path, "w")
        json.dump(["1.3.6.1.4.1.14519.5.2.1.252597325734813272307930406542368112556"], anonymization_uids_met_file)
        anonymization_uids_met_file.close()
        verification = data_tracker.dicom_has_already_been_looked_into(data_path)
        self.assertTrue(verification)

    def test_add_instance_uid_to_anonymized_uids_met(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        data_tracker.add_instance_uid_to_anonymized_uids_met(data_path, with_anonymization=False)
        anonymized_uids_met_file = open(data_tracker.anonymized_uids_met_path, "r")
        anonymized_uids_met_list = json.loads(anonymized_uids_met_file.read())
        anonymized_uids_met_file.close()
        self.assertEqual(["1.3.6.1.4.1.14519.5.2.1.252597325734813272307930406542368112556"], anonymized_uids_met_list)
        data_tracker.add_instance_uid_to_anonymized_uids_met(data_path, with_anonymization=False)
        anonymized_uids_met_file = open(data_tracker.anonymized_uids_met_path, "r")
        anonymized_uids_met_list = json.loads(anonymized_uids_met_file.read())
        anonymized_uids_met_file.close()
        self.assertEqual(["1.3.6.1.4.1.14519.5.2.1.252597325734813272307930406542368112556"], anonymized_uids_met_list)
        data_tracker.add_instance_uid_to_anonymized_uids_met(data_path, with_anonymization=True)
        anonymized_uids_met_file = open(data_tracker.anonymized_uids_met_path, "r")
        anonymized_uids_met_list = json.loads(anonymized_uids_met_file.read())
        anonymized_uids_met_file.close()
        self.assertEqual(["1.3.6.1.4.1.14519.5.2.1.252597325734813272307930406542368112556"], anonymized_uids_met_list)
        anonymization_uids_met_file = open(data_tracker.anonymized_uids_met_path, "w")
        json.dump([], anonymization_uids_met_file)
        anonymization_uids_met_file.close()
        data_tracker.add_instance_uid_to_anonymized_uids_met(data_path, with_anonymization=True)
        anonymized_uids_met_file = open(data_tracker.anonymized_uids_met_path, "r")
        anonymized_uids_met_list = json.loads(anonymized_uids_met_file.read())
        anonymized_uids_met_file.close()
        self.assertEqual(["1.2.826.0.1.3680043.10.424.1297314044383254387606992106650282561"], anonymized_uids_met_list)
        data_tracker.add_instance_uid_to_anonymized_uids_met(data_path, with_anonymization=False)
        anonymized_uids_met_file = open(data_tracker.anonymized_uids_met_path, "r")
        anonymized_uids_met_list = json.loads(anonymized_uids_met_file.read())
        anonymized_uids_met_file.close()
        self.assertEqual(["1.2.826.0.1.3680043.10.424.1297314044383254387606992106650282561"], anonymized_uids_met_list)
        data_tracker.add_instance_uid_to_anonymized_uids_met(data_path, with_anonymization=True)
        anonymized_uids_met_file = open(data_tracker.anonymized_uids_met_path, "r")
        anonymized_uids_met_list = json.loads(anonymized_uids_met_file.read())
        anonymized_uids_met_file.close()
        self.assertEqual(["1.2.826.0.1.3680043.10.424.1297314044383254387606992106650282561"], anonymized_uids_met_list)

    def tearDown(self) -> None:
        if os.path.exists(data_tracker.anonymized_uids_met_path):
            os.remove(data_tracker.anonymized_uids_met_path)


if __name__ == '__main__':
    unittest.main()
