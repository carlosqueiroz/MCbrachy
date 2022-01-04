LDR_BRACHY_PHYSICS = """
# ====================================================== #
#                       PHYSICS                          #
# ====================================================== #
s:Ge/World/Material     = "G4_WATER"
sv:Ph/Default/Modules                  = 1 "g4em-livermore"
b:Ph/Default/Auger                     = "True"
b:Ph/Default/AugerCascade              = "True"
b:Ph/Default/Fluorescence              = "True"
b:Ph/Default/DeexcitationIgnoreCut     = "T"
s:Ph/Default/Type = "Geant4_Modular"
sv:Ph/Default/LayeredMassGeometryWorlds = 1 "SeedsWorld"
"""