"""Writes its/patches/STMS_Cameras.cfg: hull cameras for RasterPropMonitor's camera pages (and the Avionics cockpit's monitors) and for
Hullcam VDS, after the ship views of SpaceX's flight livestreams. IDs are fixed across the mod:
  1 aft, down past the engines (HLS: landing)   2 engine bay   3, 4 aft flaps (HLS: a leg, the docking hardware)
  5, 6 forward flaps (HLS: airlock and elevator, horizon)   7 low on the nose (SEP's payload bay camera; HLS: hull looking down)   8 nose looking forward
On SEP's ship RasterPropMonitor uses SEP's own camera transforms and Hullcam keeps SEP's modules; ours is only the forward nose
camera, where SEP has none. usage: python3 make_cameras_cfg.py <out.cfg>"""
import sys
AFTER = ':AFTER[StarshipThingyMabobsAndSuch]'
# (parts, comment, our camera models, RPM cameras (id, transform), our own cameras for Hullcam (id, transform, name, FoV max, min))
SEP = [('SEP_26_SHIP_CORE|STMS_B3_CoreExp', "SEP's Block 3 ship core and our expendable copy: SEP's engine bay and aft flap cameras",
        [], [(1, 'UpperAftCameraTransform_1'), (2, 'LowerAftCameraTransform_1'), (3, 'Cam_LAft'), (4, 'Cam_RAft')], []),
       ('SEP_26_SHIP_NOSECONE|SEP_26_SHIP_CARGO|SEP_26_SHIP_PEZ|STMS_B3_NoseCrew|STMS_B3_NoseCrewCargo',
        "SEP's noses and our two crew noses: SEP's forward flap cameras and the one low on the nose, our nose camera",
        ['STMS_Cams_B3Nose'], [(5, 'LFWDCAMERA'), (6, 'RFWDCAMERA'), (7, 'Cam_PLDoor'), (8, 'stms_cam8')], [(8, 'stms_cam8', 'NoseForward', 90, 30)])]
HLS = [('STMS_HLS_Core', 'the HLS core', [(1, 'Landing'), (2, 'EngineBay'), (3, 'Leg'), (4, 'Docking')]),
       ('STMS_HLS_Crew|STMS_HLS_CrewTall', 'the HLS crew sections', [(5, 'Airlock'), (6, 'Horizon'), (7, 'HullDown'), (8, 'NoseUp')])]


def block(head, *body):
    out = ['\t' + head, '\t{']
    for b in body: out += ['\t' + l for l in b] if isinstance(b, list) else ['\t\t' + b]
    return out + ['\t}']


def rpm(i, t):
    return block('MODULE:NEEDS[RasterPropMonitor]', 'name = JSIExternalCameraSelector', f'cameraContainer = {t}', 'cameraIDPrefix = ExtCam', f'current = {i}', 'maximum = 8')


def hullcam(t, name, fmax, fmin):
    return block('MODULE:NEEDS[HullCameraVDS]', 'name = MuMechModuleHullCameraZoom', f'cameraName = {name}', f'cameraTransformName = {t}', 'cameraForward = 0, 0, 0',
                 'cameraUp = 0, 0, 0', 'cameraPosition = 0.0, 0.0, 0.0', f'cameraFoVMax = {fmax}', f'cameraFoVMin = {fmin}')


pods = block('MODULE:NEEDS[B9PartSwitch]', 'name = ModuleB9PartSwitch', 'moduleID = STMS_CamPods', 'switcherDescription = Camera pods', 'affectDragCubes = false',
             block('SUBTYPE', 'name = Shown', 'title = Shown', 'transform = stms_campods')[0:], block('SUBTYPE', 'name = Hidden', 'title = Hidden (the cameras still work)'))
o = ['// Hull cameras for RasterPropMonitor (camera pages, the Avionics cockpit\'s monitors) and Hullcam VDS. Written by its/scripts/make_cameras_cfg.py.',
     '// IDs are fixed across the mod (renumber in the part menu if a ship carries two of a kind):',
     '//   1 aft, down past the engines (HLS: landing)   2 engine bay   3, 4 aft flaps (HLS: a leg, the docking hardware)',
     '//   5, 6 forward flaps (HLS: airlock and elevator, horizon)   7 low on the nose (SEP\'s payload bay camera; HLS: hull looking down)   8 nose looking forward',
     "// On SEP's ship RasterPropMonitor uses SEP's own camera transforms and Hullcam keeps SEP's modules; ours is only the forward nose camera,",
     '// where SEP has none. Camera pods: Shown or Hidden; hidden, the cameras still work.', '']
for parts, note, models, cams, own in SEP:
    o += [f'// {note}', f'@PART[{parts}]:NEEDS[RasterPropMonitor|HullCameraVDS]{AFTER}', '{']
    for m in models: o += block('MODEL', f'model = StarshipThingyMabobsAndSuch/Parts/{m}')
    for i, t in cams: o += rpm(i, t)
    for i, t, n, a, b in own: o += hullcam(t, 'STMS' + n, a, b)
    o += (pods if models else []) + ['}']
for parts, note, cams in HLS:
    o += [f'// {note}: its own models carry the cameras and pods', f'@PART[{parts}]{AFTER}', '{']
    for i, n in cams: o += rpm(i, f'stms_cam{i}')
    for i, n in cams: o += hullcam(f'stms_cam{i}', 'HLS' + n, 100 if i == 1 else 90, 30)
    o += pods + ['}']
open(sys.argv[1], 'w').write('\n'.join(o) + '\n')
print('cameras cfg:', sys.argv[1])
