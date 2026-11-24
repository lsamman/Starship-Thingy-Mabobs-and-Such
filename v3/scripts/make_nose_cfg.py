"""Writes the Block 3 crew nosecones: ModuleManager copies of SEP_26_SHIP_NOSECONE that keep SEP's own MODEL (from the
player's install, nothing of SEP's is shipped) and add our window kit as a second MODEL.
usage: make_nose_cfg.py <out.cfg>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L

KIT = 'StarshipThingyMabobsAndSuch/Parts/'
PARTS = {
    'crew': ('STMS_B3_NoseCrew', 'STMS_B3_WindowsCrew', 'Block 3 Crew Nosecone', 2.0, 9000,
             'SEP\'s Block 3 nose with the payload space turned into cabins: the ITS crew section\'s big lattice window up top, '
             'three rows of portholes below, all on the leeward steel. The tiles stay on the windward side, where the view is mostly plasma anyway. Twelve kerbals, '
             'each with more room than they get on a space station and less than they will ask for.',
             'crew cabin window habitat passenger'),
    'crewcargo': ('STMS_B3_NoseCrewCargo', 'STMS_B3_WindowsCrewCargo', 'Block 3 Crew-Cargo Nosecone', 1.0, 4000,
                  'SEP\'s Block 3 nose with a flight deck for four behind the ITS crew section\'s big lattice window, and a row of portholes below. The barrel below is a cargo bay '
                  'with SEP\'s clamshell doors, two nodes and a light, so the payload rides downstairs and does not have to listen.',
                  'crew cabin window cargo flight deck'),
}


ITS = 'StarshipThingyMabobsAndSuch/ITS/Parts/'
SEPT = 'StarshipExpansionProject/Assets/BL3/'


import math
_a = math.radians(L.DOCK['az']); _r = L.DOCK['plate'] + .016; _z = sum(L.DOCK['z']) / 2
PORT = '\tnode_stack_port = %.4f, %.4f, %.4f, %.4f, 0, %.4f, 1' % (_r * math.sin(_a), _z, -_r * math.cos(_a), math.sin(_a), -math.cos(_a))


def anim(clip, what):
    return [f'\t\tanimationName = {clip}', f'\t\tactionGUIName = Toggle {what}', f'\t\tstartEventGUIName = Open {what}', f'\t\tendEventGUIName = Close {what}', '\t\tallowDeployLimit = true', '\t\trevClampDirection = true', '\t\tevaDistance = 6']


def slots(cargo):
    """A cargo bay finds its doors by module index, so the animations take over SEP's first two modules in place: its
    (doorless) bay and its Ablative switch, which comes back at the end."""
    first, second = (('stmsDoors', 'Cargo Doors'), ('stmsDock', 'Docking Door')) if cargo else (('stmsDock', 'Docking Door'), ('stmsEva', 'EVA Hatch'))
    bay = lambda i, r, y, x=0, z=0: ['\tMODULE', '\t{', '\t\tname = ModuleCargoBay', f'\t\tDeployModuleIndex = {i}', '\t\tclosedPosition = 0', f'\t\tlookupRadius = {r}', f'\t\tlookupCenter = {x:.3f}, {y}, {z:.3f}', '\t}']
    o = ['\t@MODULE[ModuleCargoBay]', '\t{', '\t\t@name = ModuleAnimateGeneric', '\t\t!DeployModuleIndex = DEL', '\t\t!closedPosition = DEL', '\t\t!lookupRadius = DEL', '\t\t!lookupCenter = DEL'] + anim(*first) + ['\t}',
         '\t@MODULE[ModuleB9PartSwitch]:HAS[#moduleID[SEP_Ablative]]', '\t{', '\t\t@name = ModuleAnimateGeneric', '\t\t!moduleID = DEL', '\t\t!switcherDescription = DEL', '\t\t!affectDragCubes = DEL', '\t\t!SUBTYPE,* {}'] + anim(*second) + ['\t}']
    if cargo: o += ['\tMODULE', '\t{', '\t\tname = ModuleAnimateGeneric'] + anim('stmsEva', 'EVA Hatch') + ['\t}'] + bay(0, 2.5, -1.3)
    o += bay(1 if cargo else 0, 0.75, round(_z, 3), _r * math.sin(_a), -_r * math.cos(_a))
    if cargo: o += ['\tMODULE', '\t{', '\t\tname = ModuleLight', '\t\tlightName = stms_baylight', '\t\tuseAnimationDim = true', '\t\tlightBrightenSpeed = 2.5', '\t\tlightDimSpeed = 2.5', '\t\tresourceAmount = 0.05', '\t\tuseResources = true', '\t}']
    o += ['\tMODULE', '\t{', '\t\tname = ModuleB9PartSwitch', '\t\tmoduleID = SEP_Ablative', '\t\tswitcherDescription = #LOC_SEP_switcher_Ablative_description', '\t\taffectDragCubes = false']
    for n, t in (('39', 'default'), ('43', 'extended')): o += ['\t\tSUBTYPE', '\t\t{', f'\t\t\tname = {n}', f'\t\t\ttitle = #LOC_SEP_switcher_{t}', f'\t\t\ttransform = Ablative {n}', '\t\t}']
    return o + ['\t}']


def textures(cargo):
    """The cut pieces carry stand-in textures; B9 gives them SEP's own, from SEP's folder, so nothing loads twice."""
    sets = [('Ship_Core_7', ['stms_nose', 'stms_dockskin', 'stms_evaskin'], True, True), ('TILES', ['stms_tilesA', 'stms_tilesB'], False, False)]
    if cargo: sets += [('Ship_Core_11', ['stms_barrel', 'stms_door0_1', 'stms_door1_1'], True, True), ('Ship_Core_11', ['stms_barrelin', 'stms_door0_0', 'stms_door1_0'], True, False), ('Ship_Core_1', ['stms_pin'], True, True)]
    o = ['\tMODULE', '\t{', '\t\tname = ModuleB9PartSwitch', '\t\tmoduleID = STMS_Hull', '\t\tswitcherDescription = Hull', '\t\taffectDragCubes = false', '\t\tSUBTYPE', '\t\t{', '\t\t\tname = SEP', '\t\t\ttitle = SEP steel']
    for nm, tr, metal, ao in sets:
        for suf, prop in [('BASE', '_MainTex'), ('NRM', '_BumpMap')] + ([('MASK', '_MetalMap')] if metal else []) + ([('MASK', '_AOMap')] if ao else []):
            o += ['\t\t\tTEXTURE', '\t\t\t{', f'\t\t\t\ttexture = {SEPT}SEP_B3_{nm}_{suf}', f'\t\t\t\tshaderProperty = {prop}'] + (['\t\t\t\tisNormalMap = true'] if suf == 'NRM' else []) + [f'\t\t\t\ttransform = {t}' for t in tr] + ['\t\t\t}']
    return o + ['\t\t}', '\t}']


def lines(variant):
    name, kit, title, dm, dc, desc, tags = PARTS[variant]
    crew = L.NOSE_CREW[variant]
    cargo = variant == 'crewcargo'; hull = {'crew': 'STMS_B3_HullCrew', 'crewcargo': 'STMS_B3_HullCrewCargo'}[variant]
    o = [f'+PART[SEP_26_SHIP_NOSECONE]:NEEDS[StarshipExpansionProject]:AFTER[StarshipExpansionProject]', '{',
         f'\t@name = {name}', '\t@author = Questin, Kari (nosecone); lsamman (cabin)',
         '\tMODEL', '\t{', f'\t\tmodel = {KIT}{kit}', '\t}', '\tMODEL', '\t{', f'\t\tmodel = {ITS}{hull}', '\t}',
         PORT] + (['\tnode_stack_cargo = 0, -2.5159, 0, 0, 1, 0, 3', '\tnode_stack_cargotop = 0, -0.15, 0, 0, -1, 0, 2'] if cargo else []) + [
         f'\t@title = {title}', '\t@manufacturer = Starship Thingy Mabobs and Such',
         f'\t@description = <#ef7b06>Needs SEP: this is its Block 3 nosecone with our windows on it.</color> {desc}',
         f'\t@tags = starship sep block3 v3 nose nosecone ship {tags}',
         f'\t@mass += {dm}', f'\t@cost += {dc}', f'\t@entryCost += {dc * 2}',
         f'\tCrewCapacity = {crew}', '\tINTERNAL', '\t{', '\t\tname = ' + {'crew': 'STMS_IVA_Crew', 'crewcargo': 'STMS_IVA_CrewCargo'}[variant], '\t}',
         # SEP's meshes that the cut copies in our hull model replace, and its box colliders, which would close the openings
         '\tMODULE', '\t{', '\t\tname = ModuleB9DisableTransform'] + [f'\t\ttransform = {t}' for t in ['Nose_7_EXT', 'Tiles', '.Colliders', 'Interior_Mesh_10'] + (['Cylinder'] if cargo else [])] + ['\t}',
         '\t!MODULE[MuMechModuleHullCameraZoom],* {}'] + slots(cargo) + textures(cargo) + [
         '\tMODULE', '\t{', '\t\tname = ModuleCommand', '\t\tminimumCrew = 1', '\t\tdefaultControlPointDisplayName = Forward', '\t\thasHibernation = True', '\t}',
         '\tMODULE', '\t{', '\t\tname = ModuleScienceExperiment', '\t\texperimentID = crewReport', '\t\texperimentActionName = #autoLOC_502009',
         '\t\tresetActionName = #autoLOC_502010', '\t\treviewActionName = #autoLOC_502200', '\t\tuseStaging = False', '\t\tuseActionGroups = True',
         '\t\thideUIwhenUnavailable = True', '\t\trerunnable = True', '\t\txmitDataScalar = 1.0', '\t\tusageReqMaskInternal = 5', '\t\tusageReqMaskExternal = -1', '\t}',
         '\tMODULE', '\t{', '\t\tname = ModuleScienceContainer', '\t\treviewActionName = Review Data', '\t\tstoreActionName = Store Experiments',
         '\t\tevaOnlyStorage = True', '\t\tstorageRange = 2.0', '\t\tallowRepeatedSubjects = True', '\t}',
         # the ITS crew section's cabin lights, but only on our glass: SEP's hull materials have an _Emissive slot too
         '\tMODULE', '\t{', '\t\tname = ModuleColorChanger', '\t\tshaderProperty = _EmissiveColor', '\t\tincludedRenderer = stms_b3_glass',
         '\t\tanimRate = 0.8', '\t\tanimState = false', '\t\tuseRate = true', '\t\ttoggleInEditor = true', '\t\ttoggleInFlight = true',
         '\t\ttoggleAction = true', '\t\tunfocusedRange = 5', '\t\ttoggleName = Toggle Cabin Lights', '\t\teventOnName = Cabin Lights: On',
         '\t\teventOffName = Cabin Lights: Off', '\t\tdefaultActionGroup = Light',
         '\t\tredCurve', '\t\t{', '\t\t\tkey = 0 0 0 3', '\t\t\tkey = 1 1 0 0', '\t\t}',
         '\t\tgreenCurve', '\t\t{', '\t\t\tkey = 0 0 0 1', '\t\t\tkey = 1 1 1 0', '\t\t}',
         '\t\tblueCurve', '\t\t{', '\t\t\tkey = 0 0 0 0', '\t\t\tkey = 1 0.9 1.5 0', '\t\t}',
         '\t\talphaCurve', '\t\t{', '\t\t\tkey = 0 1', '\t\t}', '\t}',
         '}']
    return o


out = ['// Generated by v3/scripts/make_nose_cfg.py; edit there. Needs Starship Expansion Project: these parts show its',
       '// Block 3 nosecone model from the player\'s own install. Window rows, crew numbers: v3/scripts/layout.py.']
for v in PARTS:
    out += lines(v)
open(sys.argv[1], 'w').write('\n'.join(out) + '\n')
print('nose cfg:', ', '.join(p[0] for p in PARTS.values()))
