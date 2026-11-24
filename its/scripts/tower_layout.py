"""Numbers for the arms on SLE's launch tower, KSP metres, in the frame of SLE_SS_OLIT_Core (Blender axes, Unity z = y).
The ship stands on SLE's pad or table: the offset is the same in the user's craft files (SEP Block 3 stack, window side
toward the tower), measured from them."""
SHIP = (-20.897, -.330)             # ship's axis
NOSE_Z = 69.683                     # origin of SEP's Block 3 nose
CORE_Z = 58.2835                    # origin of SEP's Block 3 ship core
EVA_Z = NOSE_Z + .96                # sill of our noses' EVA hatch
QD_Z = CORE_Z - 10.02               # middle of the ship's quick disconnect plate
CREW, QD = (.70, -5.51), (-.70, 5.51)  # where the arms bolt on: outer faces of the two side columns (a corner of the tower faces the ship)
HULL = 2.8125
