"""Numbers for the arms on SLE's launch tower, KSP metres, in the frame of the tower core part as it stands in game (Blender
axes, Unity z = y). SLE's model carries a root scale KSP drops, so these come from the user's craft files, not the .mu."""
SHIP = (-20.897, -.330)             # ship's axis
NOSE_Z, CORE_Z, BOOST_Z = 69.683, 58.2835, 24.199      # origins of SEP's Block 3 nose, ship core, booster
HULL = 2.8125
EVA_Z = NOSE_Z + .96                # sill of our noses' EVA hatch
QD_Z = CORE_Z - 10.02               # middle of the ship's quick disconnect plate
NODE = (5.3835, .7566, 46.5577)     # SLE's free node (connect02) on the rear column: the only one the chopstick carriage leaves bare
NODE_N = (.990268, .139173)         # its direction
SCALE = .98854                      # SLE model to game
MZ = (-3.2796, -.4622, 44.629)      # chopsticks part in this frame, as the user's craft carry it
# SLE's collider is one square box (8.47 m, faces at azimuth 53 and -37), so a radial part sits square to a face, never on the corner.
FACE_AZ, FACE_R, FACE_T = -37.0, 4.235 * SCALE, 3.55        # the face the crew arm goes on; FACE_T along it lands on the rear column
import math as _m
CREW = (FACE_R * _m.cos(_m.radians(FACE_AZ)) - FACE_T * _m.sin(_m.radians(FACE_AZ)), FACE_R * _m.sin(_m.radians(FACE_AZ)) + FACE_T * _m.cos(_m.radians(FACE_AZ)))
