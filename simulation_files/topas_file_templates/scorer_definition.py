from string import Template

CLINICAL_DOSE_GRID = Template("""
# ====================================================== #
#                         SCORER                         #
# ====================================================== #
s:Ge/DoseGrid/Type       = "TsBox"
s:Ge/DoseGrid/Parent     = "World"
d:Ge/DoseGrid/HLX        = ${hlx} mm
d:Ge/DoseGrid/HLY        = ${hly} mm
d:Ge/DoseGrid/HLZ        = ${hlz} mm
i:Ge/DoseGrid/XBins      = ${nb_of_columns}
i:Ge/DoseGrid/YBins      = ${nb_of_rows}
i:Ge/DoseGrid/ZBins      = ${nb_of_slices}
d:Ge/DoseGrid/TransX             = ${transx} mm
d:Ge/DoseGrid/TransY             = ${transy} mm
d:Ge/DoseGrid/TransZ             = ${transz} mm
d:Ge/DoseGrid/RotX               = ${rotx} deg
d:Ge/DoseGrid/RotY               = ${roty} deg
d:Ge/DoseGrid/RotZ               = ${rotz} deg
b:Ge/DoseGrid/IsParallel = "T"

d:Sc/DoseOnRTGrid/OnlyIncludeParticlesWithInitialKEAbove : 5. keV
s:Sc/DoseOnRTGrid/Quantity                   = "DoseToMedium"
s:Sc/DoseOnRTGrid/Component                  = "DoseGrid"

b:Sc/DoseOnRTGrid/OutputToConsole            = "F"
s:Sc/DoseOnRTGrid/IfOutputFileAlreadyExists  = "Increment"
s:Sc/DoseOnRTGrid/OutputType                 = "DICOM"
b:Sc/DoseOnRTGrid/DICOMOutput32BitsPerPixel  = "True"
s:Sc/DoseOnRTGrid/OutputFile                 = "${output_path}"
""")