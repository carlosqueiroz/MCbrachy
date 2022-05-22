import os

from dicom_rt_context_extractor.sources_information_extraction import extract_all_sources_informations
from dicom_rt_context_extractor.utils.search_instance_and_convert_coord_in_pixel import find_modality_in_folder
from prostate_calcification_segmentation.calcification_segmentation import segmenting_calcification


class DicomExtractors:
    def __init__(self, input_file_folder, **kwargs):
        """

        :param input_file_folder:
        :param kwargs: for egs_brachy, kwargs must have nb_treads (int), waiting_time (float) and
                       egs_brachy_home (str)
        """
        self.input_file_folder = input_file_folder
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

        self.permanent_implant_brachy = self._extract_permanent_implant_brachy_context
        self.hdr_brachy = self._extract_hdr_brachy_context
        self.ldr_brachy = self._extract_ldr_brachy_context

    def _extract_permanent_implant_brachy_context(self, output_folder: str) -> str:
        pass

    def _extract_hdr_brachy_context(self, output_folder: str) -> str:
        pass

    def _extract_ldr_brachy_context(self, output_folder: str):
        rt_plan_path = find_modality_in_folder("RTPLAN", self.input_file_folder)
        plan = extract_all_sources_informations(rt_plan_path)
        plan.extract_structures(self.input_file_folder)
        plan.extract_dosimetry(self.input_file_folder)
        if hasattr(self, "segmentation"):
            if "prostate_calcification" in self.__getattribute__("generate_dvh"):
                self._segment_prostate_calcification(plan, output_folder)

        return plan

    def extract_context_from_dicoms(self, treatment_modality: str, output_folder: str):
        assert treatment_modality in ["permanent_implant_brachy", "hdr_brachy", "ldr_brachy"]
        self.__getattribute__(treatment_modality)(output_folder)

    def _segment_prostate_calcification(self, plan, output_folder):
        prostate_calcification_mask = segmenting_calcification(plan, 1.9, self.input_file_folder)
        plan.structures.add_mask_from_3d_array(prostate_calcification_mask,
                                               roi_name="prostate_calcification",
                                               observation_label="masking sources with cylindrical masks with"
                                                                 " thresholding",
                                               segmentation_method=1, add_to_original_rt_struct_file=True,
                                               saving_path=os.path.join(output_folder,
                                                                        f"updated_{plan.patient}_{plan.study}"
                                                                        f"_RTSTRUCT.dcm")
                                               )
