from simulation_files.topas_file_templates.materials import *

# TODO attenteion à changer
MATERIAL_CONVERTER = {"Target": "TG186Prostate",
                      "Bladder": "TG186MeanMaleSoftTissue",
                      "Rectum": "Air",
                      "Urethra": "TG186MeanMaleSoftTissue",
                      "Bladder Neck": "TG186MeanMaleSoftTissue",
                      "calcification": "CALCIFICATION_ICRU46"}

MATERIAL_DEFINITION_TABLE = {"TG186Prostate": TG186Prostate,
                             "TG186MeanAdipose": TG186MeanAdipose,
                             "TG186MeanGland": TG186MeanGland,
                             "TG186MeanMaleSoftTissue": TG186MeanMaleSoftTissue,
                             "TG186MeanFemaleSoftTissue": TG186MeanFemaleSoftTissue,
                             "TG186MeanSkin": TG186MeanSkin,
                             "TG186CorticalBone": TG186CorticalBone,
                             "TG186EyeLens": TG186EyeLens,
                             "TG186LungInflated": TG186LungInflated,
                             "TG186Liver": TG186Liver,
                             "TG186Heart": TG186Heart,
                             "TG186Water": TG186Water,
                             "CALCIFICATION_ICRU46": CALCIFICATION_ICRU46}
