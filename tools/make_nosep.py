"""Writes a copy of the packaged mod with nothing of SEP's in it: no files derived from SEP's art, no copies of or patches on SEP's
parts, no paths into SEP's folder. Part names stay. usage: make_nosep.py <GameData/mod> <out dir>  (out dir must not exist)"""
import glob, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
dst = os.path.join(out, 'GameData', os.path.basename(src)); shutil.copytree(src, dst, ignore=shutil.ignore_patterns('@thumbs'))
p = lambda *a: os.path.join(dst, *a)
rd = lambda f: open(p(f), encoding='utf-8').read()
def wr(f, t): open(p(f), 'w', encoding='utf-8').write(t)
def sub(f, *prs):
    t = rd(f)
    for a, b in prs:
        assert a in t, (f, a); t = t.replace(a, b)
    wr(f, t)

# ---------------- gone
GONE = ['Textures', 'docs', 'ITS/Patches/ITS_Rings.cfg', 'ITS/Patches/STMS_Docking.cfg', 'ITS/Patches/STMS_Variants.cfg', 'Patches/SEPX_V3_*', 'Patches/STMS_B3_*',
        'Patches/STMS_FwdRCS.cfg', 'Parts/STMS_B3_*', 'Parts/stms_b3_*', 'ITS/Parts/SEP_B3_*', 'ITS/Parts/STMS_B3_Hull*',
        'ITS/Parts/STMS_FwdRCS_B*', 'ITS/Parts/STMS_RacewayCap.mu', 'ITS/Parts/STMS_B3_CargoAwning.mu', 'ITS/Patches/STMS_B3_CargoAwning.cfg', 'ITS/Parts/STMS_IVA_Crew*', 'ITS/Patches/STMS_IVA_Crew*', 'ITS/Parts/ITS_Ring*Base.mu',
        'ITS/Parts/stms_plain*']
for g in GONE:
    fs = glob.glob(p(g)); assert fs, g
    for f in fs: shutil.rmtree(f) if os.path.isdir(f) else os.remove(f)

# ---------------- configs
f = 'ITS/Parts/STMS_Ship_Leg.cfg'
sub(f, ("<#ef7b06>Goes on the four leg nodes this mod adds to SEP's Block 3 ship core, or anywhere on its barrel.</color>", '<#ef7b06>Attaches anywhere on a 5.6 m barrel.</color>'))
t = rd('ITS/Parts/STMS_HLS_Core.cfg'); n = re.sub(r'Mounts three sea-level and three vacuum Raptor 3s from SEP[^\n]*', 'Mounts three sea-level and three vacuum engines of your choice, with a docking node on the far side.', t); assert n != t; wr('ITS/Parts/STMS_HLS_Core.cfg', n)
sub('ITS/Parts/STMS_B3_Depot.cfg', ('<#ef7b06>Goes on the Expendable Block 3 Core.</color>', '<#ef7b06>Goes on the Starship HLS Core.</color>'),
    ("Meets them with SEP's docking hardware on the core", 'Meets them with a docking port on the core'))
sub('ITS/Parts/STMS_HLS_Depot.cfg', ('<#ef7b06>Goes on the Block 3 Expendable Core with its Hull set to White.</color>', '<#ef7b06>Goes on any 5.6 m tank.</color>'), (" Tankers dock to SEP's hardware on the core.", ''))
sub('ITS/Parts/STMS_B3_FairingBase.cfg', ('Closes off the top of the Expendable Block 3 Core with', 'Closes off the top of the Starship HLS Core with'))
sub('Parts/SEP_CW_Parts.cfg', ('winch node on the V3 cargo bay ceiling', 'winch node on the HLS cargo section ceiling'))
sub('ITS/Patches/STMS_HLS.cfg', ("a tenth of the boiloff of SEP's tanks", 'little boiloff'))
t = rd('ITS/Patches/ITS_Mods.cfg'); wr('ITS/Patches/ITS_Mods.cfg', t[:t.index("// The parts sit in SEP's category")].replace('|ITS_Ring*|ITS_RVac', ''))
sub('ITS/Extras/ITS_PBR.cfg.txt', (", so the hull matches SEP's engines under Deferred", ''))
sub('ITS/Patches/ITS_Waterfall.cfg', ("Engine plumes come with SEP's engines.", ''))
for f in glob.glob(p('**', '*.cfg'), recursive=True):
    t = open(f, encoding='utf-8').read(); n = re.sub(r'(tags = [^\n]*)\bsep ', r'\1', t)
    if n != t: open(f, 'w', encoding='utf-8').write(n)
cut = {'STMS_HLS_Docking_M', 'STMS_HLS_Docking_F', 'STMS_B3_CoreExp', 'STMS_B3_NoseCrew', 'STMS_B3_NoseCrewCargo', 'STMS_HLS_Cargo', 'STMS_B3_CargoAwning', 'ITS_Ring21', 'ITS_Ring14', 'ITS_Ring7', 'ITS_RVac'}
t = rd('Patches/STMS_CCK.cfg').replace("// after the copies of SEP's parts (engine rings, crew nosecones) exist\n", '')
wr('Patches/STMS_CCK.cfg', re.sub(r'@PART\[(STMS_HLS_Core[^\]]*)\]', lambda m: '@PART[' + '|'.join(q for q in m[1].split('|') if q not in cut) + ']', t))
# the fairing base's forward thrusters, always on
wr('Patches/STMS_FwdRCS.cfg', '''// Forward-facing RCS on the fairing base.
@PART[STMS_B3_FairingBase]:LAST[StarshipThingyMabobsAndSuch]
{
	MODEL
	{
		model = StarshipThingyMabobsAndSuch/ITS/Parts/STMS_FwdRCS_FB
	}
	MODULE
	{
		name = ModuleRCSFX
		thrusterTransformName = STMS_FwdRCS
		thrusterPower = 34
		resourceFlowMode = STAGE_PRIORITY_FLOW
		stagingEnabled = False
		enablePitch = False
		enableYaw = False
		enableRoll = False
		enableX = False
		enableY = False
		enableZ = True
		PROPELLANT
		{
			name = LqdMethane
			ratio = 3
			DrawGauge = True
		}
		PROPELLANT
		{
			name = Oxidizer
			ratio = 1
		}
		atmosphereCurve
		{
			key = 0 290
			key = 1 160
			key = 5 0.001
		}
	}
}
@PART[STMS_B3_FairingBase]:NEEDS[Waterfall]:LAST[StarshipThingyMabobsAndSuch]
{
	MODULE
	{
		name = ModuleWaterfallFX
		moduleID = stmsFwdRcsFX
		CONTROLLER
		{
			name = rcs
			linkedTo = rcs
			thrusterTransformName = STMS_FwdRCS
		}
		CONTROLLER
		{
			name = atmosphereDepth
			linkedTo = atmosphere_density
		}
		TEMPLATE
		{
			templateName = waterfall-rcs-jet-1
			overrideParentTransform = STMS_FwdRCS
			position = 0,0,0
			rotation = 0, 0, 180
			scale = 2.5, 2.5, 2.5
		}
	}
}
''')
wr('README.md', '''# Starship Thingy Mabobs and Such, standalone edition

The same mod without the Starship Expansion Project (SEP): no files made from it, no copies of its parts, and it does not need to be installed. Part names are the same as in the full mod, so install **one or the other**, never both.

## In it

ITS 2016 (booster, ship, crew, cargo and tanker sections, grid fins, legs, solar fans, crane), Starship HLS (core, crew and awning cargo sections, legs, shrouds, elevator, solar arrays, crane frame, floors, tray), cargo winch, depot, payload plate and fairing, Block 3 leg, crew access arm and ship QD arm.

## Not in it

These were SEP's parts or changes to them: the Raptors and ITS engine rings, the Block 3 crew noses, the expendable core, the bay-door HLS cargo section, the white docking hardware, and forward RCS on SEP's noses. **There are no main engines here: put any engines you like on the engine nodes.** The HLS's landing thrusters are included. Craft that use the missing parts will not load.

## Needs

ModuleManager, B9PartSwitch and Community Resource Pack. Breaking Ground for the winch, crane, elevator, floors and tray; SimpleAdjustableFairings for the fairing; HabTechProps for the HLS interior. Resurfaced and Shabby give the HLS parts their materials. Optional: Waterfall, StagedAnimation, StarshipLaunchExpansion (the tower the arms fit).
''')
t = rd('LICENSE'); i = t.index('The V3 mask textures'); wr('LICENSE', t[:i].rstrip() + '\n\nNothing in this edition is derived from Starship Expansion Project art.\n')
left = [f for f in glob.glob(p('**', '*'), recursive=True) if os.path.isfile(f) and not f.endswith(('README.md', 'LICENSE', '.dds')) and re.search(rb'StarshipExpansion|SEP_(?!CW_)|\bSEP\b(?!_CW|\.CW)', open(f, 'rb').read())]
print('mentions of SEP left:', [os.path.relpath(f, dst) for f in left])
