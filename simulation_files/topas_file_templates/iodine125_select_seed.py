from string import Template

HEADER = """
#                                                          #
#                 Iodine 125 - Select Seed                 #
#                                                          #
#                                                          #
#                Latest version - May 2021                 #
#                Author: Francisco Berumen                 #
#              Contact - fberumenm@gmail.com               #
#       https://doi.org/10.1016/j.brachy.2020.12.007       #
#                                                          #
"""

MATERIALS = """
##### MATERIAL DEFINITION ######
sv:Ma/MatTitaniumTube/Components = 1 "Titanium"
uv:Ma/MatTitaniumTube/Fractions  = 1 1
d:Ma/MatTitaniumTube/Density     = 4.51 g/cm3

sv:Ma/MatRadioactiveLayer/Components = 3 "Silver" "Chlorine" "Iodine"
uv:Ma/MatRadioactiveLayer/Fractions  = 3 0.557 0.083 0.360
d:Ma/MatRadioactiveLayer/Density     = 5.64 g/cm3

sv:Ma/MatSilverRod/Components = 1 "Silver"
uv:Ma/MatSilverRod/Fractions  = 1 1
d:Ma/MatSilverRod/Density     = 10.5 g/cm3

iv:Gr/Color/transparentgray = 4 255 255 255 100
iv:Gr/Color/transparentgray2 = 4 200 200 200 100
"""

SEEDS = Template("""
s:Ge/SelectSeed${index}/Type              = "Group"
s:Ge/SelectSeed${index}/Parent            = "World"
b:Ge/SelectSeed${index}/IsParallel        = "True"
s:Ge/SelectSeed${index}/ParallelWorldName = "SeedsWorld"
d:Ge/SelectSeed${index}/TransX            = ${position_x} mm
d:Ge/SelectSeed${index}/TransY            = ${position_y} mm
d:Ge/SelectSeed${index}/TransZ            = ${position_z} mm

##### TITANIUM TUBE
s:Ge/SelectSeedTitaniumTube${index}/Type         = "TsCylinder"
s:Ge/SelectSeedTitaniumTube${index}/Material     = "MatTitaniumTube"
s:Ge/SelectSeedTitaniumTube${index}/Parent       = "SelectSeed${index}"
d:Ge/SelectSeedTitaniumTube${index}/RMin         = 0 mm
d:Ge/SelectSeedTitaniumTube${index}/RMax         = 0.4 mm
d:Ge/SelectSeedTitaniumTube${index}/HL           = 1.85 mm
d:Ge/SelectSeedTitaniumTube${index}/SPhi         = 0. deg
d:Ge/SelectSeedTitaniumTube${index}/DPhi         = 360. deg
s:Ge/SelectSeedTitaniumTube${index}/Color        = "transparentgray2"
s:Ge/SelectSeedTitaniumTube${index}/DrawingStyle = "Solid"
b:Ge/SelectSeedTitaniumTube${index}/IsParallel        = "True"
s:Ge/SelectSeedTitaniumTube${index}/ParallelWorldName = "SeedsWorld"

##### TITANIUM CAP L
s:Ge/SelectSeedTitaniumCapL${index}/Type         = "TsSphere"
s:Ge/SelectSeedTitaniumCapL${index}/Material     = "MatTitaniumTube"
s:Ge/SelectSeedTitaniumCapL${index}/Parent       = "SelectSeed${index}"
d:Ge/SelectSeedTitaniumCapL${index}/RMin         = 0. mm
d:Ge/SelectSeedTitaniumCapL${index}/RMax         = 0.4 mm
d:Ge/SelectSeedTitaniumCapL${index}/SPhi         = 0. deg
d:Ge/SelectSeedTitaniumCapL${index}/DPhi         = 360. deg
d:Ge/SelectSeedTitaniumCapL${index}/STheta       = 0. deg
d:Ge/SelectSeedTitaniumCapL${index}/DTheta       = 90. deg
d:Ge/SelectSeedTitaniumCapL${index}/TransZ       = 1.85 mm
s:Ge/SelectSeedTitaniumCapL${index}/DrawingStyle = "Solid"
s:Ge/SelectSeedTitaniumCapL${index}/Color        = "transparentgray2"
b:Ge/SelectSeedTitaniumCapL${index}/IsParallel        = "True"
s:Ge/SelectSeedTitaniumCapL${index}/ParallelWorldName = "SeedsWorld"

##### TITANIUM CAP R
s:Ge/SelectSeedTitaniumCapR${index}/Type         = "TsSphere"
s:Ge/SelectSeedTitaniumCapR${index}/Material     = "MatTitaniumTube"
s:Ge/SelectSeedTitaniumCapR${index}/Parent       = "SelectSeed${index}"
d:Ge/SelectSeedTitaniumCapR${index}/RMin         = 0. mm
d:Ge/SelectSeedTitaniumCapR${index}/RMax         = 0.4 mm
d:Ge/SelectSeedTitaniumCapR${index}/SPhi         = 0. deg
d:Ge/SelectSeedTitaniumCapR${index}/DPhi         = 360. deg
d:Ge/SelectSeedTitaniumCapR${index}/STheta       = 90. deg
d:Ge/SelectSeedTitaniumCapR${index}/DTheta       = 180. deg
d:Ge/SelectSeedTitaniumCapR${index}/TransZ       = -1.85 mm
s:Ge/SelectSeedTitaniumCapR${index}/DrawingStyle = "Solid"
s:Ge/SelectSeedTitaniumCapR${index}/Color        = "transparentgray2"
b:Ge/SelectSeedTitaniumCapR${index}/IsParallel        = "True"
s:Ge/SelectSeedTitaniumCapR${index}/ParallelWorldName = "SeedsWorld"

##### AIR
s:Ge/SelectSeedInsideAir${index}/Type         = "TsCylinder"
s:Ge/SelectSeedInsideAir${index}/Material     = "G4_AIR"
s:Ge/SelectSeedInsideAir${index}/Parent       = "SelectSeedTitaniumTube${index}"
d:Ge/SelectSeedInsideAir${index}/RMin         = 0 mm
d:Ge/SelectSeedInsideAir${index}/RMax         = Ge/SelectSeedTitaniumTube${index}/RMax - 0.05 mm
d:Ge/SelectSeedInsideAir${index}/HL           = 1.85 mm
d:Ge/SelectSeedInsideAir${index}/SPhi         = 0. deg
d:Ge/SelectSeedInsideAir${index}/DPhi         = 360. deg
s:Ge/SelectSeedInsideAir${index}/Color        = "transparentgray"
s:Ge/SelectSeedInsideAir${index}/DrawingStyle = "Solid"
b:Ge/SelectSeedInsideAir${index}/IsParallel        = "True"
s:Ge/SelectSeedInsideAir${index}/ParallelWorldName = "SeedsWorld"

##### RADIOACTIVE LAYER
s:Ge/SelectSeedRadioactiveLayer${index}/Type         = "TsCylinder"
s:Ge/SelectSeedRadioactiveLayer${index}/Material     = "MatRadioactiveLayer"
s:Ge/SelectSeedRadioactiveLayer${index}/Parent       = "SelectSeedInsideAir${index}"
d:Ge/SelectSeedRadioactiveLayer${index}/RMin         = 0 mm
d:Ge/SelectSeedRadioactiveLayer${index}/RMax         = 0.258 mm
d:Ge/SelectSeedRadioactiveLayer${index}/HL           = 1.703 mm
d:Ge/SelectSeedRadioactiveLayer${index}/SPhi         = 0. deg
d:Ge/SelectSeedRadioactiveLayer${index}/DPhi         = 360. deg
b:Ge/SelectSeedRadioactiveLayer${index}/Invisible    = "True"
b:Ge/SelectSeedRadioactiveLayer${index}/IsParallel        = "True"
s:Ge/SelectSeedRadioactiveLayer${index}/ParallelWorldName = "SeedsWorld"

##### CYLINDRICAL SILVER ROD
s:Ge/SelectSeedSilverRod${index}/Type         = "TsCylinder"
s:Ge/SelectSeedSilverRod${index}/Material     = "MatSilverRod"
s:Ge/SelectSeedSilverRod${index}/Parent       = "SelectSeedRadioactiveLayer${index}"
d:Ge/SelectSeedSilverRod${index}/RMin         = 0 mm
d:Ge/SelectSeedSilverRod${index}/RMax         = Ge/SelectSeedRadioactiveLayer${index}/RMax - 0.003 mm
d:Ge/SelectSeedSilverRod${index}/HL           = Ge/SelectSeedRadioactiveLayer${index}/HL - 0.003 mm
d:Ge/SelectSeedSilverRod${index}/SPhi         = 0. deg
d:Ge/SelectSeedSilverRod${index}/DPhi         = 360. deg
s:Ge/SelectSeedSilverRod${index}/Color        = "White"
s:Ge/SelectSeedSilverRod${index}/DrawingStyle = "Solid"
b:Ge/SelectSeedSilverRod${index}/IsParallel        = "True"
s:Ge/SelectSeedSilverRod${index}/ParallelWorldName = "SeedsWorld"

s:So/SelectSeedActiveSource${index}/Type                       = "Volumetric"
s:So/SelectSeedActiveSource${index}/Component                  = "SelectSeedRadioactiveLayer${index}"
sc:So/SelectSeedActiveSource${index}/ActiveMaterial            = "MatRadioactiveLayer"
s:So/SelectSeedActiveSource${index}/BeamParticle               = "gamma"
ic:So/SelectSeedActiveSource${index}/NumberOfHistoriesInRun    = ${photon_per_seed}
i:So/SelectSeedActiveSource${index}/MaxNumberOfPointsToSample  = 1000000000
s:So/SelectSeedActiveSource${index}/BeamEnergySpectrumType     = "Discrete"

#### I-125 SPECTRUM ####
dv:So/SelectSeedActiveSource${index}/BeamEnergySpectrumValues = 7 3.77 27.202 27.472 30.944 30.995 31.704 35.4922 keV
uv:So/SelectSeedActiveSource${index}/BeamEnergySpectrumWeightsUnscaled = 7 0.149 0.401 0.740 0.0683 0.132 0.0380 0.0668
uv:So/SelectSeedActiveSource${index}/BeamEnergySpectrumWeights = 0.626919 * So/SelectSeedActiveSource${index}/BeamEnergySpectrumWeightsUnscaled
""")


