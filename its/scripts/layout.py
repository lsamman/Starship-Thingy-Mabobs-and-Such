"""Numbers shared by build scripts, configs and checks. KSP metres unless named real. Part frames are Blender's (x, y, z)."""
import math
import hull as H
K = H.K
RV_SCALE = 1.35                      # SEP's vacuum Raptor is 1.44 m across; the slide's is about 2 m at this scale
R3_TOP, R3_VAC_EXIT = 1.81, -0.92    # SEP_26_RAPTOR_3's own nodes
Z_EXIT = (0 - H.O_AFT) * K           # vacuum engines' exit plane in the aft section's frame
VAC_R = H.R_VAC * K
VAC_AZ = [30 + 60 * i for i in range(6)]
VAC_Z = Z_EXIT + (R3_TOP - R3_VAC_EXIT) * RV_SCALE
SL_R = 1.15 * K
SL_AZ = [0, 120, 240]
SL_Z = Z_EXIT + R3_TOP + .03
AFT_TOP = (H.Z_SPLIT - H.O_AFT) * K
AFT_BOT = (H.Z_LEE - H.O_AFT) * K
FWD_BOT = (H.Z_SPLIT - H.O_FWD) * K

# booster, real metres: z = 0 at the engines' exit, 77.5 at the top of the interstage
BZ_TOP, B_ORIGIN = 77.5, 38.75
BR = 6.0
B_BASE = 0.55
B_INTER = 72.2                       # floor of the interstage; the ship's engines hang into it
B_CUT = 73.0                         # interstage wall is cut down to here on the windward side for the ship's skirt
RINGS = {'ITS_Ring21': (21, 5.21 * K, 0.0), 'ITS_Ring14': (14, 3.59 * K, 360 / 28), 'ITS_Ring7': (6, 1.56 * K, 0.0)}
B_ENG = (0 - B_ORIGIN) * K + R3_TOP + .03    # ring node height in the booster's frame
GF_AZ = [0, 120, 240]                # over the base fairings (slides 33 and 34, landing render)
RW_AZ = [60, 180, 300]               # raceways between them
GF_Z = 66.2                          # real, hinge of the stowed grid fins

# details atlas (pixels, origin top left of 2048)
DET = {
    'white': (0, 0, 512, 512), 'grey': (512, 0, 512, 512), 'carbon': (1024, 0, 512, 512), 'steel': (1536, 0, 512, 512),
    'dark': (0, 512, 512, 512), 'alu': (512, 512, 512, 512), 'black': (1024, 512, 512, 512), 'invar': (1536, 512, 512, 512),
    'wall': (0, 1024, 1024, 512), 'deck': (1024, 1024, 512, 512), 'stripe': (1536, 1024, 512, 256), 'hatch': (1536, 1280, 512, 256),
    'pica': (0, 1536, 512, 512), 'dome': (512, 1536, 512, 512), 'copper': (1024, 1536, 256, 256), 'rubber': (1280, 1536, 256, 256),
    'cable': (1024, 1792, 512, 128), 'lamp': (1024, 1920, 256, 128), 'label': (1536, 1536, 512, 512),
}

# booster sheet: 120 degrees repeated three times, in two strips
B_STRIP = ((B_BASE, 39.0), (39.0, BZ_TOP))
B_PAD = .004
FLAG = (1536 + 8, 1536 + 8, 440, 232)    # flag art inside the label zone


def b_uv(az, z, strip):
    """Booster sheet coordinate. az must be given relative to the segment's own start (0..120)."""
    z0, z1 = B_STRIP[strip]
    return strip * .5 + B_PAD + (.5 - 2 * B_PAD) * az / 120, B_PAD + (1 - 2 * B_PAD) * (z - z0) / (z1 - z0)


def b_top(az):
    """Top edge of the interstage wall, real metres: follows the ship's skirt."""
    return 77.5 - H.Z_STAGE + H.skirt_z(az) - .05

# landing legs, real metres in the plane of a fairing: hinge on the sloping lower face, sole height with the leg out
LEG_AZ = [0, 120, 240]
LEG_H = (8.80, 12.80)                    # radius, z
LEG_SOLE = -4.3
LEG_TILT = 16.0                          # deployed strut, degrees outboard of vertical
LEG_STOW = math.degrees(math.atan2(H.R_RIDGE - H.RB, H.Z_R2 - H.Z_R3))   # the face's own slope, inboard going down

# fan arrays: stowed against the inside of the skirt, pivot just inside its lower edge (real metres)
FAN_AZ = [60, 300]
FAN_P = (H.RB - .16, 5.75)

# cargo section, real metres
BAY_FLOOR, BAY_TOP, DOOR_AZ = 28.5, 40.4, 60
DOOR_Z = (28.7, 40.3)
LINER = .30

# crane, KSP metres: the boom runs along azimuth CR_AZ, so the platform comes down beside the leeward foot
CR_AZ = 25
CR_RAIL_X, CR_RAIL_Y, CR_MID_Y, CR_ARM_Y = 1.0, (-2.45, 2.35), (-2.35, 2.30), (-.95, 2.25)
CR_SHARE, CR_C, CR_TRAVEL = .55, -.40, 6.8
CR_Z = dict(tie=(-.17, -.07), rail=(-.37, -.17), beam=(-.59, -.43))
CR_CABLE, CR_DECK, CR_APEX, CR_DECK_W, CR_DECK_D, CR_HOIST = -.95, -3.05, 1.95, 2.6, 2.5, 25.6
