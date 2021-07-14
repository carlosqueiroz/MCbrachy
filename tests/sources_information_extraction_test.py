import logging
import os
import unittest

from extraction_pipeline_components.sources_information_extraction import extract_sources_positions, \
    extract_sources_context_information, extract_all_sources_informations
from root import ROOT

test_log_filename = os.path.join(ROOT, "logs", "test_logs")
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, "tests", "test_data")


class TestExtractSourcesPositions(unittest.TestCase):
    def test_with_HDR_no_orientations(self):
        path_to_rt_plan = os.path.join(data_folder, "HDR.dcm")
        dict_of_pos = extract_sources_positions(path_to_rt_plan)
        self.assertEqual(dict_of_pos[1]["positions"].shape, (19, 3))
        self.assertEqual(dict_of_pos[1]["orientations"].shape, (19, 0))

    def test_not_rt_plan(self):
        path_to_rt_plan = os.path.join(data_folder, "RTSTRUCT.dcm")
        dict_of_pos = extract_sources_positions(path_to_rt_plan)
        self.assertEqual({}, dict_of_pos)

    def test_with_LDR_no_orientations(self):
        path_to_rt_plan = os.path.join(data_folder, "test_patient", "study", "rt_plan", "RTPLAN104.dcm")
        dict_of_pos = extract_sources_positions(path_to_rt_plan)
        self.assertEqual(dict_of_pos[1]["positions"].shape, (36, 3))
        self.assertEqual(dict_of_pos[1]["orientations"].shape, (36, 0))


class TestExtractSourcesContexInformation(unittest.TestCase):
    def test_with_HDR(self):
        path_to_rt_plan = os.path.join(data_folder, "HDR.dcm")
        dict_of_context = extract_sources_context_information(path_to_rt_plan)
        self.assertEqual(dict_of_context['RTPlanDate'], '20210525')
        self.assertEqual(dict_of_context['RTPlanTime'], 150321.0)
        self.assertEqual(dict_of_context['RefRtStructUID'],
                         '1.2.826.0.1.3680043.10.424.5797527849867755087781141160218741500')
        self.assertEqual(dict_of_context['RTPlan'],
                         '1.2.826.0.1.3680043.10.424.1107485761079427425525033230406408940')
        self.assertEqual(dict_of_context["RefRtDoseUID"],
                         '1.2.826.0.1.3680043.10.424.1312788673205172322354485444433063857')
        self.assertEqual(dict_of_context[1]['SourceIsotopeName'], 'Ir-192')
        self.assertEqual(dict_of_context[1]['ReferenceAirKermaRate'], 20460.908203125)
        self.assertEqual(dict_of_context[1]['SourceStrengthReferenceDate'], '20210525')
        self.assertEqual(dict_of_context[1]['SourceStrengthReferenceTime'], 134342.0)
        self.assertEqual(dict_of_context[1]['MaterialID'], 'Stainless Steel')
        self.assertEqual(dict_of_context[1]['SourceType'], 'CYLINDER')
        self.assertEqual(dict_of_context[1]['SourceManufacturer'], 'Nucletron B.V.')
        self.assertEqual(dict_of_context[1]['ActiveSourceDiameter'], 0.60000002384185)
        self.assertEqual(dict_of_context[1]['ActiveSourceLength'], 3.5)

    def test_not_rt_plan(self):
        path_to_rt_plan = os.path.join(data_folder, "RTSTRUCT.dcm")
        dict_of_context = extract_sources_context_information(path_to_rt_plan)
        self.assertEqual({}, dict_of_context)

    def test_with_LDR(self):
        path_to_rt_plan = os.path.join(data_folder, "test_patient", "study", "rt_plan", "RTPLAN104.dcm")
        dict_of_context = extract_sources_context_information(path_to_rt_plan)
        self.assertEqual(dict_of_context['RTPlan'],
                         '1.2.826.0.1.3680043.10.424.1326279788265105019278215552609106950')
        self.assertEqual(dict_of_context["RefRtStructUID"],
                         '1.2.826.0.1.3680043.10.424.6377455315485968017200746515229809227')
        self.assertEqual(dict_of_context["RefRtDoseUID"],
                         '1.2.826.0.1.3680043.10.424.3347861674843696263926395926853075079')
        self.assertEqual(dict_of_context['RTPlanDate'], '20170615')
        self.assertEqual(dict_of_context['RTPlanTime'], 181054.0)
        self.assertEqual(dict_of_context['RefRtStructUID'],
                         '1.2.826.0.1.3680043.10.424.6377455315485968017200746515229809227')
        self.assertEqual(dict_of_context[1]['SourceIsotopeName'], 'I-125')
        self.assertEqual(dict_of_context[1]['ReferenceAirKermaRate'], 0.75205701589584)
        self.assertEqual(dict_of_context[1]['SourceStrengthReferenceDate'], '20170302')
        self.assertEqual(dict_of_context[1]['SourceStrengthReferenceTime'], 120000.0)
        self.assertEqual(dict_of_context[1]['MaterialID'], 'Stainless Steel')
        self.assertEqual(dict_of_context[1]['SourceType'], 'CYLINDER')
        self.assertEqual(dict_of_context[1]['SourceManufacturer'], 'Nucletron B.V.')
        self.assertEqual(dict_of_context[1]['ActiveSourceDiameter'], 0.60000002384185)
        self.assertEqual(dict_of_context[1]['ActiveSourceLength'], 3.40000009536743)


class TestAllSourcesInformations(unittest.TestCase):
    def test_with_HDR(self):
        path_to_rt_plan = os.path.join(data_folder, "HDR.dcm")
        LDR_plan = extract_all_sources_informations(path_to_rt_plan)
        self.assertEqual(LDR_plan.rt_plan_date, '20210525')
        self.assertEqual(LDR_plan.rt_plan_time, 150321.0)
        self.assertEqual(LDR_plan.rt_plan_uid,
                         '1.2.826.0.1.3680043.10.424.1107485761079427425525033230406408940')
        self.assertEqual(LDR_plan.rt_dose_uid,
                         '1.2.826.0.1.3680043.10.424.1312788673205172322354485444433063857')
        self.assertEqual(LDR_plan.rt_struct_uid,
                         '1.2.826.0.1.3680043.10.424.5797527849867755087781141160218741500')
        self.assertEqual(LDR_plan.list_of_sources[0].source_isotope_name, 'Ir-192')
        self.assertEqual(LDR_plan.list_of_sources[0].air_kerma_rate, 20460.908203125)
        self.assertEqual(LDR_plan.list_of_sources[0].ref_date, '20210525')
        self.assertEqual(float(LDR_plan.list_of_sources[0].ref_time), 134342.0)
        self.assertEqual(LDR_plan.list_of_sources[0].material, 'Stainless Steel')
        self.assertEqual(LDR_plan.list_of_sources[0].source_type, 'CYLINDER')
        self.assertEqual(LDR_plan.list_of_sources[0].source_manufacturer, 'Nucletron B.V.')
        self.assertEqual(LDR_plan.list_of_sources[0].source_diameter, 0.60000002384185)
        self.assertEqual(LDR_plan.list_of_sources[0].source_lenght, 3.5)
        self.assertEqual(LDR_plan.list_of_sources[0].positions.shape, (19, 3))
        self.assertEqual(LDR_plan.list_of_sources[0].orientations.shape, (19, 0))

    def test_no_rt_plan(self):
        path_to_rt_plan = os.path.join(data_folder, "RTSTRUCT.dcm")
        LDR_plan = extract_all_sources_informations(path_to_rt_plan)
        self.assertEqual(None, LDR_plan)

    def test_with_LDR(self):
        path_to_rt_plan = os.path.join(data_folder, "test_patient", "study", "rt_plan", "RTPLAN104.dcm")
        LDR_plan = extract_all_sources_informations(path_to_rt_plan)
        self.assertEqual(LDR_plan.rt_plan_date, '20170615')
        self.assertEqual(LDR_plan.rt_plan_time, 181054.0)
        self.assertEqual(LDR_plan.rt_plan_uid,
                         '1.2.826.0.1.3680043.10.424.1326279788265105019278215552609106950')
        self.assertEqual(LDR_plan.rt_struct_uid,
                         '1.2.826.0.1.3680043.10.424.6377455315485968017200746515229809227')
        self.assertEqual(LDR_plan.rt_dose_uid,
                         '1.2.826.0.1.3680043.10.424.3347861674843696263926395926853075079')

        self.assertEqual(LDR_plan.list_of_sources[0].source_isotope_name, 'I-125')
        self.assertEqual(LDR_plan.list_of_sources[0].air_kerma_rate,  0.75205701589584)
        self.assertEqual(LDR_plan.list_of_sources[0].ref_date, '20170302')
        self.assertEqual(float(LDR_plan.list_of_sources[0].ref_time), 120000.0)
        self.assertEqual(LDR_plan.list_of_sources[0].material, 'Stainless Steel')
        self.assertEqual(LDR_plan.list_of_sources[0].source_type, 'CYLINDER')
        self.assertEqual(LDR_plan.list_of_sources[0].source_manufacturer, 'Nucletron B.V.')
        self.assertEqual(LDR_plan.list_of_sources[0].source_diameter, 0.60000002384185)
        self.assertEqual(LDR_plan.list_of_sources[0].source_lenght, 3.40000009536743)
        self.assertEqual(LDR_plan.list_of_sources[0].positions.shape, (36, 3))
        self.assertEqual(LDR_plan.list_of_sources[0].orientations.shape, (36, 0))


if __name__ == '__main__':
    unittest.main()
