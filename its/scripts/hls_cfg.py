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
    part('STMS_HLS_Core', 'Starship HLS Core', 'The Moon-bound ship\'s tanks, engine bay and legwork. White insulating tiles instead of a heat shield, no flaps, and a black belt of eighteen landing thrusters two thirds of the way up, so the last hundred metres are flown without digging a crater under yourself. Mounts three sea-level and three vacuum Raptor 3s from SEP, stacks on SEP\'s Block 3 booster, and takes SEP\'s ship-to-ship docking hardware on the far side from the elevator.',
         T + ' core tank methalox engine mount landing thruster', 21.0, 31000, 'FuelTank', 'veryHeavyRocketry', profiles='size4p5', crash=20, tmax=2000, skin=2000, brk=5000,
         extra=['fuelCrossFeed = True', 'vesselType = Ship', fx],
         modules=[tank(82000),
                  mod('ModuleEnginesFX', 'engineID = landing', 'thrustVectorTransformName = landingThrust', 'runningEffectName = landing', 'exhaustDamage = False', 'ignitionThreshold = 0.1', 'minThrust = 0', 'maxThrust = 540',
                      'heatProduction = 0', 'EngineType = LiquidFuel', 'allowShutdown = True', 'stagingEnabled = False', 'engineAccelerationSpeed = 6', 'engineDecelerationSpeed = 8', 'useEngineResponseTime = True',
                      block('PROPELLANT', 'name = LqdMethane', 'ratio = 3', 'DrawGauge = True'), block('PROPELLANT', 'name = Oxidizer', 'ratio = 1'), block('atmosphereCurve', 'key = 0 340', 'key = 1 220', 'key = 6 0.001')),
                  rcs(34), command(0), sas(), res('ElectricCharge', 3000), wheel(150, 1.5), antenna(500000), light('baseLight'),
                  cc(['lampglow', 'navgreen', 'navred'], 'Exterior Lights: On', 'Exterior Lights: Off', 'Exterior Lights'),
                  mod('ModuleToggleCrossfeed', 'crossfeedStatus = true', 'toggleEditor = true', 'toggleFlight = true')])
    sol = lambda t: mod('ModuleDeployableSolarPanel', f'animationName = solar{t}', f'pivotName = sol{t}pivot', f'raycastTransformName = sol{t}catch', f'secondaryTransformName = sol{t}catch', 'isTracking = true', 'sunAlignFactor = 1',
                        'retractable = true', 'isBreakable = false', 'resourceName = ElectricCharge', 'chargeRate = 14', 'showStatus = true', 'bypassAnimations = false', 'trackingSpeed = 0.2')
    anim = lambda a, on, off, what, grp='None': mod('ModuleAnimateGeneric', f'animationName = {a}', f'actionGUIName = Toggle {what}', f'startEventGUIName = {on}', f'endEventGUIName = {off}', f'defaultActionGroup = {grp}', 'allowDeployLimit = false', 'evaDistance = 6')
    part('STMS_HLS_Crew', 'Starship HLS Crew Section', 'Cabins behind a row of ten windows, an airlock the size of a garage under an awning door, and a nose cap that tips back off a docking port so visitors from Orion can come in the front. Two solar arrays roll out of the side hatches. The deck is a long way up; the elevator is sold separately and is not optional.',
         T + ' crew cabin window airlock nose docking port solar command', 13.0, 42000, 'Pods', 'veryHeavyRocketry', rules='1,0,1,1,0', profiles='size4p5', crash=14, tmax=2000, skin=2000, brk=5000,
         extra=['CrewCapacity = 8', 'vesselType = Lander', RCS_FX, block('INTERNAL', 'name = MK3_CrewCab_Int')],
         modules=[anim('noseCap', 'Open Nose Cap', 'Close Nose Cap', 'Nose Cap'),
                  mod('ModuleDockingNode', 'nodeTransformName = dockPort', 'controlTransformName = dockPort', 'nodeType = B10_APAS, size1', 'deployAnimationController = 0', 'deployAnimationTarget = 1', 'stagingEnabled = False', 'acquireRange = 0.6', 'captureRange = 0.08'),
                  anim('doorOpen', 'Open Airlock Door', 'Close Airlock Door', 'Airlock Door'), sol(1), sol(2),
                  command(0), sas(), res('ElectricCharge', 3000), wheel(150, 1), antenna(5000000), tank(1950), rcs(34), light('doorLight'),
                  cc(['windows', 'lampglow'], 'Cabin Lights: On', 'Cabin Lights: Off', 'Cabin Lights'),
                  G['livery']('HLS_Markings', 'Markings', [('Flag', 'Flag', 'gray', ['flag']), ('None', 'Plain', 'white', [])]),
                  mod('ModuleScienceContainer', 'reviewActionName = Review Data', 'storeActionName = Store Experiments', 'evaOnlyStorage = True', 'storageRange = 2.0', 'allowRepeatedSubjects = True'),
                  mod('ModuleInventoryPart', 'InventorySlots = 12', 'packedVolumeLimit = 2400'),
                  mod('ModuleKerbNetAccess', 'MinimumFoV = 5', 'MaximumFoV = 50', 'enhancedSituationMask = 7', 'requiresAnimation = False', block('DISPLAY_MODES', 'Mode = Terrain', 'Mode = Biome'))])
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
    part('STMS_HLS_Lift', 'Starship HLS Elevator', f'<#ef7b06>Goes on the node in the crew section\'s airlock.</color> Open the airlock door, lower the deck, then slide Target Extension to -{HL.LIFT_TRAVEL} to ride the track down to the surface, and back to 0 before folding the deck and closing the door. Needs Breaking Ground. If it sulks, there is a ladder down the same track.',
         T + ' elevator lift winch platform', .5, 3200, 'Payload', 'veryHeavyRocketry', rules='1,0,0,1,0', profiles='size1, srf', crash=14, skin=1900, brk=1500,
         modules=[G['piston']('LiftAnchor', 'LiftServo', 'cargo', HL.LIFT_TRAVEL, 1.0, 1.5, 'Y'), anim('deckFold', 'Lower Deck', 'Fold Deck', 'Elevator Deck')])
