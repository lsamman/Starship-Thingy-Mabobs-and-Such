"""Part configs for Starship HLS, with make_cfg.py's helpers. Masses on SEP's scale (its Block 3 core is 25 t with tiles
and flaps and holds 82000 B9 units)."""
import math
import hls_layout as HL


def write(G):
    part, mod, block, res, command, sas, wheel, antenna, RCS_FX, SND, have, f5 = [G[k] for k in ('part', 'mod', 'block', 'res', 'command', 'sas', 'wheel', 'antenna', 'RCS_FX', 'SND', 'have', 'f5')]
    if not have('STMS_HLS_Core'): return
    G['MFR'] = 'Starship Thingy Mabobs and Such'
    T = 'starship sep hls moon lunar lander artemis block3 v3'
    tank = lambda units: mod('ModuleB9PartSwitch', 'moduleID = HLS_Fuel', 'switcherDescription = Propellant', f'baseVolume = {units}',
                             block('SUBTYPE', 'name = Methalox', 'title = Methalox', 'tankType = ITSLMOX', 'primaryColor = #8fb7d9', 'secondaryColor = #e8e8e8'))
    rcs = lambda p: mod('ModuleRCSFX', 'thrusterTransformName = RCSthruster', f'thrusterPower = {p}', 'resourceFlowMode = STAGE_PRIORITY_FLOW', 'runningEffectName = running', 'stagingEnabled = False',
                        block('PROPELLANT', 'name = LqdMethane', 'ratio = 3', 'DrawGauge = True'), block('PROPELLANT', 'name = Oxidizer', 'ratio = 1'), block('atmosphereCurve', 'key = 0 310', 'key = 1 210', 'key = 4 0.001'))
    cc = lambda inc, on, off, name, auto='Light': mod('ModuleColorChanger', 'moduleID = ' + name, 'shaderProperty = _EmissiveColor', *[f'includedRenderer = {i}' for i in inc], 'animRate = 0.8', 'animState = false', 'useRate = true',
        'toggleInEditor = true', 'toggleInFlight = true', 'toggleAction = true', 'unfocusedRange = 5', f'toggleName = Toggle {name}', f'eventOnName = {on}', f'eventOffName = {off}', f'defaultActionGroup = {auto}',
        block('redCurve', 'key = 0 0 0 3', 'key = 1 1 0 0'), block('greenCurve', 'key = 0 0 0 1', 'key = 1 1 1 0'), block('blueCurve', 'key = 0 0 0 0', 'key = 1 0.95 1.5 0'), block('alphaCurve', 'key = 0 1'))
    light = lambda n: mod('ModuleLight', f'lightName = {n}', 'useAnimationDim = true', 'lightBrightenSpeed = 2.5', 'lightDimSpeed = 2.5', 'resourceAmount = 0.06', 'useResources = true')
    land_fx = block('landing', block('AUDIO', 'channel = Ship', 'clip = sound_vent_medium', 'volume = 0 0', 'volume = 1 0.9', 'pitch = 0 0.6', 'pitch = 1 0.9', 'loop = true'),
                    block('MODEL_MULTI_PARTICLE', 'modelName = Squad/FX/Monoprop_small', 'transformName = landingThrust', 'emission = 0 0', 'emission = 0.05 0.3', 'emission = 1 1', 'speed = 0 0.6', 'speed = 1 1', 'localRotation = 0, 0, 0'))
    fx = [x for x in RCS_FX]; fx = fx[:-1] + ['\t' + l for l in land_fx] + fx[-1:]
    part('STMS_HLS_Core', 'Starship HLS Core', 'The Moon-bound ship\'s tanks, engine bay and legwork. White instead of a heat shield, no flaps, and a black belt of eighteen landing thrusters two thirds of the way up, so the last hundred metres are flown without digging a crater under yourself. Mounts three sea-level and three vacuum Raptor 3s from SEP, stacks on SEP\'s Block 3 booster, and takes SEP\'s ship-to-ship docking hardware on the far side from the elevator.',
         T + ' core tank methalox engine mount landing thruster', 21.0, 31000, 'FuelTank', 'veryHeavyRocketry', profiles='size4p5', crash=20, tmax=2000, skin=2000, brk=5000,
         extra=['fuelCrossFeed = True', 'vesselType = Ship', fx],
         modules=[tank(82000),
                  mod('ModuleEnginesFX', 'engineID = landing', 'thrustVectorTransformName = landingThrust', 'runningEffectName = landing', 'exhaustDamage = False', 'ignitionThreshold = 0.1', 'minThrust = 0', 'maxThrust = 540',
                      'heatProduction = 0', 'EngineType = LiquidFuel', 'allowShutdown = True', 'stagingEnabled = False', 'engineAccelerationSpeed = 6', 'engineDecelerationSpeed = 8', 'useEngineResponseTime = True',
                      block('PROPELLANT', 'name = LqdMethane', 'ratio = 3', 'DrawGauge = True'), block('PROPELLANT', 'name = Oxidizer', 'ratio = 1'), block('atmosphereCurve', 'key = 0 340', 'key = 1 220', 'key = 6 0.001')),
                  rcs(34), command(0), sas(), res('ElectricCharge', 3000), wheel(150, 1.5), antenna(500000), light('baseLight'),
                  cc(['lampglow', 'navgreen', 'navred'], 'Exterior Lights: On', 'Exterior Lights: Off', 'Exterior Lights'),
                  mod('ModuleToggleCrossfeed', 'crossfeedStatus = true', 'toggleEditor = true', 'toggleFlight = true'),
                  G['livery']('HLS_Style', 'Style', [('Original', 'Original', 'black', ['hull_o', 'bells_o', 'ducts_o']), ('R2024', '2024 render', 'white', ['hull', 'bells', 'ducts', 'legpods', 'legpods_in'] + [f'col_pod{a}{k}' for a in HL.LEG_AZ for k in 'abt'])]),
                  G['livery']('HLS_Track', 'Elevator track', [('Rails', 'Rails and ladder', 'gray', ['track', 'ladder']), ('None', 'None (cargo)', 'white', [])])])
    anim = lambda a, on, off, what, grp='None': mod('ModuleAnimateGeneric', f'animationName = {a}', f'actionGUIName = Toggle {what}', f'startEventGUIName = {on}', f'endEventGUIName = {off}', f'defaultActionGroup = {grp}', 'allowDeployLimit = false', 'evaDistance = 6')
    part('STMS_HLS_Crew', 'Starship HLS Crew Section', 'Cabins behind a row of ten windows, an airlock the size of a garage under an awning door, and a nose cap that tips back off a flat seat for a docking port. Four bays in the sides take roll-out solar arrays. The deck is a long way up; the elevator is sold separately and is not optional.',
         T + ' crew cabin window airlock nose docking seat command', 13.0, 42000, 'Pods', 'veryHeavyRocketry', rules='1,0,1,1,0', profiles='size4p5', crash=14, tmax=2000, skin=2000, brk=5000,
         extra=['CrewCapacity = 8', 'vesselType = Lander', RCS_FX, block('INTERNAL', 'name = STMS_IVA_HLS')],
         modules=[anim('noseCap', 'Open Nose Cap', 'Close Nose Cap', 'Nose Cap'),
                  mod('ModuleCargoBay', 'DeployModuleIndex = 0', 'closedPosition = 0', 'lookupRadius = 0.95', 'lookupCenter = 0, 10.75, 0'),
                  anim('doorOpen', 'Open Airlock Door', 'Close Airlock Door', 'Airlock Door'),
                  command(0), sas(), res('ElectricCharge', 3000), wheel(150, 1), antenna(5000000), tank(1950), rcs(34), light('doorLight'),
                  cc(['windows', 'lampglow'], 'Cabin Lights: On', 'Cabin Lights: Off', 'Cabin Lights'),
                  G['livery']('HLS_Markings', 'Markings', [('Flag', 'Flag', 'gray', ['flag']), ('None', 'Plain', 'white', [])]),
                  mod('ModuleScienceContainer', 'reviewActionName = Review Data', 'storeActionName = Store Experiments', 'evaOnlyStorage = True', 'storageRange = 2.0', 'allowRepeatedSubjects = True'),
                  mod('ModuleInventoryPart', 'InventorySlots = 12', 'packedVolumeLimit = 2400'),
                  mod('ModuleKerbNetAccess', 'MinimumFoV = 5', 'MaximumFoV = 50', 'enhancedSituationMask = 7', 'requiresAnimation = False', block('DISPLAY_MODES', 'Mode = Terrain', 'Mode = Biome')),
                  mod('ModuleB9PartSwitch', 'moduleID = HLS_Style', 'switcherDescription = Style', 'affectDragCubes = false',
                      block('SUBTYPE', 'name = Original', 'title = Original', 'primaryColor = black', block('TEXTURE', 'texture = StarshipThingyMabobsAndSuch/ITS/Parts/hls_crew_o_diff', 'shaderProperty = _MainTex', 'transform = hull', 'transform = doorskin', 'transform = capskin')),
                      block('SUBTYPE', 'name = R2024', 'title = 2024 render', 'primaryColor = white'))])
    sun = lambda i: mod('ModuleDeployableSolarPanel', 'isTracking = false', f'pivotName = cargoSun{i}', f'raycastTransformName = cargoSun{i}', f'secondaryTransformName = cargoSun{i}', 'isBreakable = false', 'sunAlignFactor = 1', 'resourceName = ElectricCharge', 'chargeRate = 5', 'showStatus = true')
    part('STMS_HLS_CargoAwning', 'Starship HLS Cargo Section (Awning Door)', 'Goes on the HLS core instead of the crew section, with nobody aboard to complain about the elevator. One wide door swings up over the bay. Put the Crane Frame on the node by the sill and the Cargo Winch Hoist under its crossbar (or the Boom on the ceiling), open the door, run it out, and it sets its load down beside the hull. Solar panels round the back keep the lights on. Set the core\'s elevator track to None.',
         T + ' cargo bay delivery uncrewed', 8.0, 26000, 'Payload', 'veryHeavyRocketry', rules='1,0,1,1,0', profiles='size4p5', crash=14, tmax=2000, skin=2000, brk=5000,
         extra=['vesselType = Lander', block('MODEL', 'model = StarshipThingyMabobsAndSuch/ITS/Parts/STMS_HLS_CargoKit'), RCS_FX],
         modules=[anim('CargoDoor', 'Open Cargo Door', 'Close Cargo Door', 'Cargo Door'),
                  mod('ModuleCargoBay', 'DeployModuleIndex = 0', 'closedPosition = 0', 'lookupRadius = 2.7', 'lookupCenter = 0, -0.1, 0', 'nodeInnerAft = cargo', 'nodeInnerFore = winch'),
                  res('ElectricCharge', 2000), rcs(34), sun(0), sun(1), sun(2), light('cargoLight'), cc(['cargo_lamps'], 'Bay Lights: On', 'Bay Lights: Off', 'Bay Lights'),
                  mod('ModuleB9DisableTransform', 'transform = cargo_sill'), G['livery']('HLS_Markings', 'Markings', [('Flag', 'Flag', 'gray', ['flag']), ('None', 'Plain', 'white', [])])])
    part('STMS_HLS_Leg', 'Starship HLS Landing Leg', 'One of four. Hangs folded down its black panel, then swings out, telescopes and puts an octagonal pad on the regolith, held by a strut to either side. Use four, on the marked nodes.',
         T + ' landing leg gear ground', .6, 4500, 'Ground', 'veryHeavyRocketry', rules='1,0,0,0,0', profiles='srf, size1', crash=30, skin=2000, brk=3000,
         extra=[block('EFFECTS', block('deploy', SND('elev_start'), SND('elev_loop', True)), block('deployed', SND('elev_stop')), block('retract', SND('elev_start'), SND('elev_loop', True, .6)), block('retracted', SND('elev_stop', False, .75)))],
         modules=[mod('ModuleWheelBase', 'wheelColliderTransformName = wheelCollider', 'useNewFrictionModel = true', 'wheelType = LEG', 'adherentStart = 0.01', 'frictionAdherent = 0.1', 'peakStart = 2', 'frictionPeak = 1.0', 'limitStart = 7.0',
                      'frictionLimit = 1.0', 'FitWheelColliderToMesh = False', 'radius = 0.30', 'center = 0,0,0', 'mass = 0.4', 'autoFrictionAvailable = False', 'clipObject = piston_collider', 'TooltipTitle = Landing Leg', 'TooltipPrimaryField =',
                      f'groundHeightOffset = {f5(HL.HINGE[1] - HL.SOLE)}'),
                  mod('ModuleWheelSuspension', 'baseModuleIndex = 0', 'suspensionTransformName = piston', 'suspensionColliderName = piston_collider', 'suspensionDistance = 0.32', 'suspensionOffset = -0.32', 'maximumLoad = 120.0', 'targetPosition = 1.0',
                      'springRatio = 28', 'damperRatio = 2.0', 'boostRatio = 0.6', 'useDistributedMass = true'),
                  mod('ModuleWheelDeployment', 'baseModuleIndex = 0', 'animationTrfName = leg', 'animationStateName = legDeploy', 'deployedPosition = 1', 'deployTargetTransformName = deployTgt', 'retractTransformName = piston', 'TsubSys = 0.87',
                      'extendDurationFactor = 0.6', 'retractDuractionFactor = 0.6', 'fxDeploy = deploy', 'fxRetract = retract', 'fxDeployed = deployed', 'fxRetracted = retracted'),
                  mod('ModuleWheelLock', 'maxTorque = 500'),
                  mod('ModuleWheelBogey', 'baseModuleIndex = 0', 'bogeyTransformName = foot', 'deployModuleIndex = 2', 'maxPitch = 20', 'minPitch = -20', 'restPitch = 0', 'pitchResponse = 100', 'bogeyAxis = 1, 0, 0', 'bogeyUpAxis = 0, 1, 0'),
                  mod('ModuleWheelDamage', 'baseModuleIndex = 0', 'stressTolerance = 99999999', 'impactTolerance = 1200', 'deflectionMagnitude = 1', 'deflectionSharpness = 2.0', 'slipMagnitude = 0', 'slipSharpness = 2.0', 'explodeMultiplier = 1.0')])
    part('STMS_HLS_LegFaired', 'Starship HLS Landing Leg (Faired)', 'One of four. White, for the core\'s 2024 render style. Hangs folded inside its fairing, then swings out, telescopes and puts an octagonal pad on the regolith, held by a strut to either side. Use four, on the marked nodes.',
         T + ' landing leg gear ground', .6, 4500, 'Ground', 'veryHeavyRocketry', rules='1,0,0,0,0', profiles='srf, size1', crash=30, skin=2000, brk=3000,
         extra=[block('EFFECTS', block('deploy', SND('elev_start'), SND('elev_loop', True)), block('deployed', SND('elev_stop')), block('retract', SND('elev_start'), SND('elev_loop', True, .6)), block('retracted', SND('elev_stop', False, .75)))],
         modules=[mod('ModuleWheelBase', 'wheelColliderTransformName = wheelCollider', 'useNewFrictionModel = true', 'wheelType = LEG', 'adherentStart = 0.01', 'frictionAdherent = 0.1', 'peakStart = 2', 'frictionPeak = 1.0', 'limitStart = 7.0',
                      'frictionLimit = 1.0', 'FitWheelColliderToMesh = False', 'radius = 0.30', 'center = 0,0,0', 'mass = 0.4', 'autoFrictionAvailable = False', 'clipObject = piston_collider', 'TooltipTitle = Landing Leg', 'TooltipPrimaryField =',
                      f'groundHeightOffset = {f5(HL.HINGE[1] - HL.SOLE)}'),
                  mod('ModuleWheelSuspension', 'baseModuleIndex = 0', 'suspensionTransformName = piston', 'suspensionColliderName = piston_collider', 'suspensionDistance = 0.32', 'suspensionOffset = -0.32', 'maximumLoad = 120.0', 'targetPosition = 1.0',
                      'springRatio = 28', 'damperRatio = 2.0', 'boostRatio = 0.6', 'useDistributedMass = true'),
                  mod('ModuleWheelDeployment', 'baseModuleIndex = 0', 'animationTrfName = leg', 'animationStateName = legDeploy', 'deployedPosition = 1', 'deployTargetTransformName = deployTgt', 'retractTransformName = piston', 'TsubSys = 0.87',
                      'extendDurationFactor = 0.6', 'retractDuractionFactor = 0.6', 'fxDeploy = deploy', 'fxRetract = retract', 'fxDeployed = deployed', 'fxRetracted = retracted'),
                  mod('ModuleWheelLock', 'maxTorque = 500'),
                  mod('ModuleWheelBogey', 'baseModuleIndex = 0', 'bogeyTransformName = foot', 'deployModuleIndex = 2', 'maxPitch = 20', 'minPitch = -20', 'restPitch = 0', 'pitchResponse = 100', 'bogeyAxis = 1, 0, 0', 'bogeyUpAxis = 0, 1, 0'),
                  mod('ModuleWheelDamage', 'baseModuleIndex = 0', 'stressTolerance = 99999999', 'impactTolerance = 1200', 'deflectionMagnitude = 1', 'deflectionSharpness = 2.0', 'slipMagnitude = 0', 'slipSharpness = 2.0', 'explodeMultiplier = 1.0')])
    part('STMS_Ship_Leg', 'Block 3 Landing Leg (Aeroshielded)', '<#ef7b06>Goes on the four leg nodes this mod adds to SEP\'s Block 3 ship core, or anywhere on its barrel.</color> A telescoping leg under a slim shell that rides out with it: the ship\'s own steel for the leeward side, tiles for the windward side. For Mars, and anywhere else the tower has not been built yet.',
         'starship sep block3 v3 mars landing leg gear ground aeroshield heat shield', .85, 6500, 'Ground', 'veryHeavyRocketry', rules='1,1,0,0,0', node_attach='0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1', profiles='srf, size1', crash=30, tmax=2000, skin=2900, brk=3000,
         extra=[block('EFFECTS', block('deploy', SND('elev_start'), SND('elev_loop', True)), block('deployed', SND('elev_stop')), block('retract', SND('elev_start'), SND('elev_loop', True, .6)), block('retracted', SND('elev_stop', False, .75)))],
         modules=[mod('ModuleWheelBase', 'wheelColliderTransformName = wheelCollider', 'useNewFrictionModel = true', 'wheelType = LEG', 'adherentStart = 0.01', 'frictionAdherent = 0.1', 'peakStart = 2', 'frictionPeak = 1.0', 'limitStart = 7.0',
                      'frictionLimit = 1.0', 'FitWheelColliderToMesh = False', 'radius = 0.30', 'center = 0,0,0', 'mass = 0.4', 'autoFrictionAvailable = False', 'clipObject = piston_collider', 'TooltipTitle = Landing Leg', 'TooltipPrimaryField =',
                      f'groundHeightOffset = {f5(HL.HINGE[1] - HL.SOLE)}'),
                  mod('ModuleWheelSuspension', 'baseModuleIndex = 0', 'suspensionTransformName = piston', 'suspensionColliderName = piston_collider', 'suspensionDistance = 0.32', 'suspensionOffset = -0.32', 'maximumLoad = 120.0', 'targetPosition = 1.0',
                      'springRatio = 28', 'damperRatio = 2.0', 'boostRatio = 0.6', 'useDistributedMass = true'),
                  mod('ModuleWheelDeployment', 'baseModuleIndex = 0', 'animationTrfName = leg', 'animationStateName = legDeploy', 'deployedPosition = 1', 'deployTargetTransformName = deployTgt', 'retractTransformName = piston', 'TsubSys = 0.87',
                      'extendDurationFactor = 0.6', 'retractDuractionFactor = 0.6', 'fxDeploy = deploy', 'fxRetract = retract', 'fxDeployed = deployed', 'fxRetracted = retracted'),
                  mod('ModuleWheelLock', 'maxTorque = 500'),
                  mod('ModuleWheelBogey', 'baseModuleIndex = 0', 'bogeyTransformName = foot', 'deployModuleIndex = 2', 'maxPitch = 20', 'minPitch = -20', 'restPitch = 0', 'pitchResponse = 100', 'bogeyAxis = 1, 0, 0', 'bogeyUpAxis = 0, 1, 0'),
                  mod('ModuleWheelDamage', 'baseModuleIndex = 0', 'stressTolerance = 99999999', 'impactTolerance = 1200', 'deflectionMagnitude = 1', 'deflectionSharpness = 2.0', 'slipMagnitude = 0', 'slipSharpness = 2.0', 'explodeMultiplier = 1.0'),
                  G['livery']('STMS_LegShell', 'Shell', [('Steel', 'Bare steel', '#b8b8bc', ['shell_steel', 'nose_steel']), ('Tiles', 'Heat shield tiles', 'black', ['shell_tile', 'nose_tile'])]),
                  mod('ModuleB9PartSwitch', 'moduleID = STMS_LegTex', 'switcherDescription = Tile texture', 'affectDragCubes = false', block('SUBTYPE', 'name = SEP', 'title = SEP tiles',
                      block('TEXTURE', 'texture = StarshipExpansionProject/Assets/BL3/SEP_B3_TILES_BASE', 'shaderProperty = _MainTex', 'transform = shell_tile', 'transform = nose_tile'),
                      block('TEXTURE', 'texture = StarshipExpansionProject/Assets/BL3/SEP_B3_TILES_NRM', 'shaderProperty = _BumpMap', 'isNormalMap = true', 'transform = shell_tile', 'transform = nose_tile')))])
    part('STMS_HLS_LegShroud', 'Starship HLS Leg Shroud', 'Keeps the airstream off a folded leg on the way up and leaves when it is no longer wanted. One per leg, on the shroud nodes of the HLS core; stage it or jettison it once out of the atmosphere, before the leg comes down.',
         T + ' leg shroud fairing jettison decoupler', .15, 900, 'Aero', 'veryHeavyRocketry', rules='1,0,0,0,0', profiles='srf, size1', crash=9, skin=2200, brk=800,
         extra=['stagingIcon = DECOUPLER_HOR', 'stageOffset = 1', 'childStageOffset = 1', 'sound_decoupler_fire = decouple'],
         modules=[mod('ModuleDecouple', 'ejectionForce = 12', 'explosiveNodeID = mount', 'menuName = Jettison Shroud', 'stagingEnabled = True'),
                  G['livery']('STMS_Shroud', 'Colour', [('Black', 'Black', 'black', ['shroud_black']), ('White', 'White', 'white', ['shroud_white'])])])
    part('STMS_HLS_Lift', 'Starship HLS Elevator', f'<#ef7b06>Goes on the node in the crew section\'s airlock.</color> Open the airlock door, lower the deck, then slide Target Extension to -{HL.LIFT_TRAVEL} to ride the track down to the surface, and back to 0 before folding the deck and closing the door. Needs Breaking Ground. If it sulks, there is a ladder down the same track.',
         T + ' elevator lift winch platform', .5, 3200, 'Payload', 'veryHeavyRocketry', rules='1,0,0,1,0', profiles='size1, srf', crash=14, skin=1900, brk=1500,
         modules=[G['piston']('LiftAnchor', 'LiftServo', 'cargo', HL.LIFT_TRAVEL, 1.0, 1.5, 'Y'), anim('deckFold', 'Lower Deck', 'Fold Deck', 'Elevator Deck')])
    part('STMS_HLS_Solar', 'Starship HLS Solar Array', 'Fourteen panels nested in a box on rails behind a flush hatch. Goes on the four bay nodes of the crew section. Tracks the sun once it is all the way out; Lock Tracking holds it still, and Rotate Array Down hangs it along the hull, locked. Do that after landing: hanging down it passes over the landing thrusters.',
         T + ' solar panel array power roll out', .25, 4200, 'Electrical', 'experimentalElectrics', rules='1,0,0,0,0', profiles='srf, size1', crash=12, skin=2000, brk=800,
         modules=[mod('ModuleDeployableSolarPanel', 'animationName = solarDeploy', 'pivotName = sunPivot', 'raycastTransformName = suncatcher', 'secondaryTransformName = suncatcher', 'isTracking = true', 'sunAlignFactor = 1',
                      'retractable = true', 'isBreakable = false', 'resourceName = ElectricCharge', 'chargeRate = 14', 'showStatus = true', 'bypassAnimations = false', 'trackingSpeed = 0.2'),
                  mod('ModuleSTMSArrayTilt', 'tiltTransform = tilt', 'downAngle = -90', 'tiltSpeed = 6', 'centreSpeed = 20')])
    if have('STMS_HLS_Crane'):
        look = block('MODULE', 'name = FXModuleLookAtConstraint', *[block('CONSTRAINLOOKFX', f'rotatorsName = {r}', f'targetName = {t}') for k in 'LR' for r, t in ((f'craneLow{k}', f'craneTip{k}'), (f'craneTop{k}', f'craneFoot{k}'))])
        part('STMS_HLS_Crane', 'Starship HLS Crane Frame', f'<#ef7b06>Goes on the crane node by the sill of the awning-door cargo section; hang the Cargo Winch Hoist under its crossbar.</color> A frame that leans out over the sill with the winch on it. Open the door, lift the load clear of the floor, then slide <b>Target Extension</b> to -{HL.CR_TRAVEL}. The slider is hidden while the piston is <b>Locked</b>. In action groups, Retract runs it out and Extend brings it in.',
             T + ' crane frame winch hoist cargo', .9, 3200, 'Payload', 'veryHeavyRocketry', rules='1,0,1,1,0', profiles='size1, srf', crash=14, skin=1900, brk=5000,
             modules=[G['piston']('CraneAnchor', 'CraneServo', 'hoist', HL.CR_TRAVEL, .25, .5, 'Z'), look])
    if have('STMS_B3_Depot'):
        import depot_layout as D
        dt = mod('ModuleB9PartSwitch', 'moduleID = HLS_Fuel', 'switcherDescription = Propellant', f'baseVolume = {D.UNITS}', block('SUBTYPE', 'name = Methalox', 'title = Methalox', 'tankType = ITSLMOX', 'percentFilled = 0', 'primaryColor = #8fb7d9', 'secondaryColor = #e8e8e8'))
        part('STMS_B3_Depot', 'Starship Depot Tank and Nose', '<#ef7b06>Goes on the Expendable Block 3 Core.</color> The storage depot: bare bright steel, no flaps, no tiles, no way home, and seven metres more tank than anything else on the pad. Launch it empty on top of a core that gets itself to orbit, then let the tankers fill it. Meets them with SEP\'s docking hardware on the core, and keeps its methane cold on its own power.',
             'starship sep hls block3 v3 storage depot tanker propellant refuel transfer orbital methalox nose', 13.0, 34000, 'FuelTank', 'veryHeavyRocketry', rules='1,0,1,1,0', profiles='size4p5', crash=14, tmax=2000, skin=2000, brk=5000,
             extra=['fuelCrossFeed = True', 'vesselType = Station', RCS_FX],
             modules=[dt, rcs(68), command(0), sas(), res('ElectricCharge', 4000), wheel(150, 1), antenna(5000000),
                      mod('ModuleDeployableSolarPanel', 'isTracking = false', 'pivotName = depotSun', 'raycastTransformName = depotSun', 'secondaryTransformName = depotSun', 'isBreakable = false', 'sunAlignFactor = 1', 'resourceName = ElectricCharge', 'chargeRate = 12', 'showStatus = true')])
    if have('STMS_CrewArm'):
        kw = dict(profiles='size2, srf', crash=80, tmax=3000, skin=3000, brk=200000)
        part('STMS_CrewArm', 'Crew Access Arm', '<#ef7b06>Attach radially to the rear column of SLE\'s tower core, the one furthest from the ship, on its face toward the crew hatch side, with the walkway level with the nose\'s EVA hatch.</color> Reaches round the chopstick carriage to the Block 3 crew noses. Its gangway, bellows, doors and white room let go one after another before it swings clear. Retract it by hand, or put it in a stage (with StagedAnimation) and it goes by itself, in ten seconds. Stage it before the engines; it stays back until the launch is reverted.',
             'starship sep sle launch tower crew access arm swing walkway white room', 8, 12000, 'Structural', 'specializedConstruction', rules='0,1,1,1,0', node_attach='0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 2',
             extra=['stagingIcon = DECOUPLER_HOR', 'stageOffset = 1', 'childStageOffset = 1'],
             modules=[mod('ModuleAnimateGeneric', 'animationName = crewArm', 'actionGUIName = Toggle Arm', 'startEventGUIName = Retract Arm', 'endEventGUIName = Extend Arm', 'allowDeployLimit = true', 'evaDistance = 30'), light('armLight'), cc(['armlamps', 'roomlamp'], 'Arm Lights: On', 'Arm Lights: Off', 'Arm Lights')], **kw)
        part('STMS_QDArm', 'Ship Quick Disconnect Arm', '<#ef7b06>Goes on the free rear node of SLE\'s tower core (five segments or more).</color> A dog-leg of black tube that reaches round the chopstick carriage to the Block 3 ship\'s quick disconnect plate, after the real one. Put it in the launch stage and it lets go and swings clear in three and a half seconds; or retract it by hand. Can top the tanks up.',
             'starship sep sle launch tower ship quick disconnect sqd qd arm fueling propellant', 10, 14000, 'Structural', 'specializedConstruction', rules='1,0,1,1,0',
             extra=['stagingIcon = DECOUPLER_HOR', 'stageOffset = 1', 'childStageOffset = 1'],
             modules=[mod('ModuleAnimateGeneric', 'animationName = qdArm', 'actionGUIName = Toggle Arm', 'startEventGUIName = Retract Arm', 'endEventGUIName = Connect Arm', 'allowDeployLimit = true', 'evaDistance = 30'),
                      mod('ModuleGenerator', 'isAlwaysActive = false', 'requiresAllInputs = false', 'resourceThreshold = 0.001', 'activateGUIName = Start Propellant Load', 'shutdownGUIName = Stop Propellant Load', block('OUTPUT_RESOURCE', 'name = LqdMethane', 'rate = 1500'), block('OUTPUT_RESOURCE', 'name = Oxidizer', 'rate = 500'))], **kw)
    if have('STMS_B3_FairingBase'):
        import fairing_layout as F
        half = lambda nm, t, m, y, h, r: block(nm, f'transformName = {t}', f'mass = {m}', f'CoM = {r:.3f}, {y + h / 2:.3f}, 0', f'rootOffset = 0, {y:.4f}, 0')
        zw = F.Z0 + F.WB
        part('STMS_B3_FairingBase', 'Block 3 Payload Plate and Fairing', 'Closes off the top of the Expendable Block 3 Core with a payload plate and a two-piece fairing that grows a segment at a time. White, smooth, and gone by the time anyone asks for it back.',
             'starship sep block3 v3 fairing payload plate adapter base SAF simple adjustable expendable', 2.4, 4200, 'Payload', 'veryHeavyRocketry', profiles='size4p5', crash=12, tmax=2000, skin=2400, brk=5000,
             extra=['stagingIcon = FUEL_TANK', 'fuelCrossFeed = True', 'stageOffset = 1', 'childStageOffset = 1', 'fx_gasBurst_white = 0.0, 0.5, 0.0, 0.0, 1.0, 0.0, deploy', 'sound_vent_large = deploy'],
             modules=[mod('ModuleSimpleAdjustableFairing', f'segmentLength = {F.WALL}', f'maxSegments = {F.SEGS}', 'numSlices = 2', 'deploySpeed = 12', f'shieldingCenter = 0, {zw / 2 + F.CONE / 2:.2f}, 0', f'shieldingBaseRadius = {(zw + F.CONE) / 2 + 1.0:.2f}', 'editorOpenOffset = 9, 0, 0', 'stagingToggleEnabledEditor = true',
                          half('WALL_BASE', 'FWallBase', .35, F.Z0, F.WB, 1.8), half('WALL', 'FWall', .38, zw, F.WALL, 1.8), half('CONE', 'FCone', .55, zw, F.CONE, 1.3),
                          block('CAP', 'transformName = FCap', 'mass = 0.03', f'CoM = 0, {zw + F.CONE + .2:.3f}, 0', f'rootOffset = 0, {zw + F.CONE:.4f}, 0')),
                      mod('ModuleCargoBay', 'DeployModuleIndex = 0', 'closedPosition = 0', f'lookupRadius = {F.R - .06:.3f}')])
