"""Writes its/patches/STMS_Cameras.cfg: hull cameras for RasterPropMonitor's camera pages (and the Avionics cockpit's monitors) and for
Hullcam VDS, after the ship views of SpaceX's flight livestreams. IDs are fixed across the mod:
  1 aft, down past the engines (HLS: landing)   2 engine bay   3, 4 aft flaps (HLS: a leg, the docking hardware)
  5, 6 forward flaps (HLS: airlock and elevator, horizon)   7, 8 payload bay, from the door and from above (HLS: hull looking down, nose looking up)
On SEP's ship these are all SEP's own cameras: RasterPropMonitor uses SEP's transforms on our copies of SEP's parts and Hullcam keeps
SEP's modules. SEP's own parts stay as SEP ships them: an RPM selector there doubled every camera in the part menu next to SEP's Hullcam
ones. The HLS's cameras are in its own models.
usage: python3 make_cameras_cfg.py <out.cfg>"""
import sys
AFTER = ':AFTER[StarshipThingyMabobsAndSuch]'
# (parts, comment, our camera models, RPM cameras (id, transform), our own cameras for Hullcam (id, transform, name, FoV max, min))
# (parts, comment, RPM cameras (id, SEP's transform))
SEP = [('STMS_B3_CoreExp', "our expendable copy of SEP's Block 3 ship core: SEP's engine bay and aft flap cameras",
        [(1, 'UpperAftCameraTransform_1'), (2, 'LowerAftCameraTransform_1'), (3, 'Cam_LAft'), (4, 'Cam_RAft')]),
       ('STMS_B3_NoseCrew|STMS_B3_NoseCrewCargo', "our two crew noses: SEP's forward flap cameras", [(5, 'LFWDCAMERA'), (6, 'RFWDCAMERA')]),
       ('STMS_B3_CargoAwning', "our awning-door copy of SEP's cargo section: SEP's flap cameras and the one by the door (the one from above now sees the top bulkhead)",
        [(5, 'LFWDCAMERA'), (6, 'RFWDCAMERA'), (7, 'Cam_PLDoor')])]
HLS = [('STMS_HLS_Core', 'the HLS core', [(1, 'Landing'), (2, 'EngineBay'), (3, 'Leg'), (4, 'Docking')]),
       ('STMS_HLS_Crew|STMS_HLS_CrewTall', 'the HLS crew sections', [(5, 'Airlock'), (6, 'Horizon'), (7, 'HullDown'), (8, 'NoseUp')])]


def block(head, *body):
    out = ['\t' + head, '\t{']
    for b in body: out += ['\t' + l for l in b] if isinstance(b, list) else ['\t\t' + b]
    return out + ['\t}']


def rpm(i, t):
    return block('MODULE:NEEDS[RasterPropMonitor]', 'name = JSIExternalCameraSelector', f'cameraContainer = {t}', 'cameraIDPrefix = ExtCam', f'current = {i}', 'maximum = 8',
                 'showCones = False')      # the FOV marker cones start off (the part menu turns them on)


def hullcam(t, name, fmax, fmin):
    return block('MODULE:NEEDS[HullCameraVDS]', 'name = MuMechModuleHullCameraZoom', f'cameraName = {name}', f'cameraTransformName = {t}', 'cameraForward = 0, 0, 0',
                 'cameraUp = 0, 0, 0', 'cameraPosition = 0.0, 0.0, 0.0', f'cameraFoVMax = {fmax}', f'cameraFoVMin = {fmin}')


pods = block('MODULE:NEEDS[B9PartSwitch]', 'name = ModuleB9PartSwitch', 'moduleID = STMS_CamPods', 'switcherDescription = Camera pods', 'affectDragCubes = false',
             block('SUBTYPE', 'name = Shown', 'title = Shown', 'transform = stms_campods')[0:], block('SUBTYPE', 'name = Hidden', 'title = Hidden (the cameras still work)'))
o = ['// Hull cameras for RasterPropMonitor (camera pages, the Avionics cockpit\'s monitors) and Hullcam VDS. Written by its/scripts/make_cameras_cfg.py.',
     '// IDs are fixed across the mod (renumber in the part menu if a ship carries two of a kind):',
     '//   1 aft, down past the engines (HLS: landing)   2 engine bay   3, 4 aft flaps (HLS: a leg, the docking hardware)',
     '//   5, 6 forward flaps (HLS: airlock and elevator, horizon)   7, 8 payload bay, from the door and from above (HLS: hull looking down, nose looking up)',
     "// SEP's ship: SEP's own cameras only (Hullcam keeps SEP's modules), on our copies of SEP's parts; SEP's own parts are left alone.",
     '// HLS: its own cameras, and a Camera pods switch (hidden, they still work).', '']
for parts, note, cams in SEP:
    o += [f'// {note}', f'@PART[{parts}]:NEEDS[RasterPropMonitor]{AFTER}', '{']
    for i, t in cams: o += rpm(i, t)
    o += ['}']
for parts, note, cams in HLS:
    o += [f'// {note}: its own models carry the cameras and pods', f'@PART[{parts}]{AFTER}', '{']
    for i, n in cams: o += rpm(i, f'stms_cam{i}')
    for i, n in cams: o += hullcam(f'stms_cam{i}', 'HLS' + n, 100 if i == 1 else 90, 30)
    o += pods + ['}']
open(sys.argv[1], 'w').write('\n'.join(o) + '\n')
print('cameras cfg:', sys.argv[1])
