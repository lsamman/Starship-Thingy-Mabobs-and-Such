# Handoff

State on 2026-11-23, 6 pm ET, written at the end of the cloud session for the user's Linux desktop. Read it first; it replaces that conversation. The model is Opus 5.5 (no Fable): Opus plans, reviews and does the hard 3D/physics work; Sonnet and Haiku take standard and bulk jobs.

## Start here on the PC

Nothing from the cloud session has been in KSP yet. On `main` (the user merged PRs #1 and #2): the pre-flight config fixes (Ring7 deletes both SEP `SEP_NODE_Switch` B9 modules; CTT patch `:LAST`; fan `isBreakable`; docking `allowRotation` dropped; cargo platform no surface attach), the cloud setup fixes, `tools/usage_plan.py`, and two SEP Block 3 crew nosecones with the ITS big lattice window: `STMS_B3_NoseCrew` (3 rows of small windows, 12 crew) and `STMS_B3_NoseCrewCargo` (1 row, 4 crew; `NOSE_SMALL_COUNT` in `v3/scripts/layout.py` for 2).

Open: PR #3, `claude/carbon-livery`: `main` + an optional B9 "Livery: White / Bare carbon" on booster, aft and the three forward sections (+54 MB), waiting for the user's verdict in game.

With KSP closed:

```
git fetch origin && git checkout claude/carbon-livery    # main + the livery; or `git checkout main` without it
./build_all.sh && ./deploy.sh
```

Then work through **Open** below with the user, ask for KSP.log lines mentioning `ITS`, `SEP_CW`, `STMS` or `StarshipThingy`, and fix what breaks. Merge PR #3 only when the user says so.

Usage: the user's weekly Claude limit resets Tue 2026-11-24 at 11 pm ET and was about 60 % used at 4 pm Monday; one full 5-hour window costs roughly 13 % of it. Have them run `/usage`, then `python3 tools/usage_plan.py --five <5h %> --week <weekly %> --five-reset HH:MM --week-reset "+1 23:00" --work "HH:MM-23:00"` for a pace.

## Starship HLS (2026-11-23 evening, branch `claude/hls`, pushed and installed on the PC, not run in KSP yet)

Built in `~/Projects/STMS-HLS`, a fresh clone, because the `.git` in `~/Projects/StarshipThingyMabobsAndSuch` is damaged (0-byte index and objects, probably a crash); the damaged repo was left as it was. Every working file there that differs from `main` matches a version already on GitHub.

Parts: `STMS_HLS_Core`, `_Crew`, `_Leg`, `_Lift`, built by the ITS pipeline (`its/scripts/hls_layout.py` numbers, `hls_common.py`, `build_hls*.py`, `tex_hls.py`, `hls_cfg.py`, `check_hls.py`; patch `its/patches/STMS_HLS.cfg`). See `docs/HLS.md`. `check_hls.py` passes, lint passes.

**After the user's first flight (2026-11-23 night):** flat docking seat with node; four separate solar parts (two panel modules on one part stopped each other); sill z-fighting; plume origin and size; glossier whites, matte blacks (`hls_det`); white docking hardware; leg shrouds; `STMS_Ship_Leg`; FreeIva shells; noses with cap, EVA hatch and, on crew-cargo, a real bay (`derive_nose.py`: SEP-derived, never commit); tower core copy, crew arm, QD arm. All of that is untested in game.

**Second feedback round (2026-11-23), not yet checked in game:** side docking door at az 30 in the steel (not the nose tip); normals of cut SEP noses carried over; slim Block 3 ship legs in SEP steel, moved off the vents; HLS solar azimuths off the airlock; HLS paint redone on SEP's Resurfaced shader; ITS tip tiles and bay gaps; masks baked per texel by azimuth; expendable core and fairing as parts (`fairing_layout.py`); QD arm and crew arm rebuilt on the rear column of SLE's normal tower (`STMS_OLIT_Core` removed, no save used it); ITS fin node .24 m lower; ITS crane deck 3.4 x 3.8 m, `CR_AZ` 28. `tower_layout.NODE` comes from the user's craft files: SLE's model measures 1.1% larger than it stands in game, cause not established. `check_arms.py` stretches the carriage upright so it stands for every height; the chopsticks themselves are not in it.


Interiors `STMS_IVA_HLS`, `STMS_IVA_Crew`, `STMS_IVA_CrewCargo` (`ivalib.py`, `iva_layout.py`, `tex_iva.py`, `render_iva.py`) replace the Mk3 placeholder on the HLS and the two Block 3 noses; check seat poses, light levels and window cameras. Note that this repo is **public** now.

To test in game: landing ring thrust direction and plume (the ring pushes up, 18 plumes point down and out); legs hold it and the pads sit level; RCS directions; elevator piston (anchor/servo names, a kerbal riding the deck, ladder); airlock EVA with the door open; nose port docks with Orion; arrays track; both light switches; SEP Raptors and booster snap on.

## What this is

**Starship Thingy Mabobs and Such**: the user's personal KSP 1.12.5 mod, add-ons for Kari's Starship Expansion Project (SEP). One installed folder, `GameData/StarshipThingyMabobsAndSuch`, built from two halves:

- `v3/`: for SEP's V3 (Block 3) ship: cargo winch for the cargo bay, an expendable config for the body (formerly "SEP Extras"), and the crew nosecones' window kits.
- `its/`: the 2016 Interplanetary Transport System, rebuilt from scratch (started as a fork of Thrimm's 2016 mod, none of its assets used).

Everything is modelled procedurally in Blender Python and textured with numpy. Generated configs, models and textures are never edited by hand.

**Status:** every ITS part is built, textured, configured and was installed on the PC before the cloud session; the final build has **not been tested in game**. An earlier phase-1 build was loaded once (rings compiled, no errors from our parts, some lag).

## The user

- New to coding; plays KSP on a Linux PC (the "Sol" install). Explain plainly and lead with the result.
- Wants photos at key milestones (they're in `docs/photos`).
- Approves useful subagents. Wants to be asked before anything public (SEP's licence forbids re-using its assets, so no fork of SEP; reference its parts by path).
- They judge looks in game. Show a render, ship it, then wait for the verdict before rolling a new look out everywhere.

Choices they made: SEP scale (real x 0.625, 7.5 m body); booster engines as ring parts only; cargo ship with side doors and a crane; placeholder IVA; the mod's name.

What they asked for, in order: upgrade the ITS mod to BDB / HabTech2 / Benjee10 Orion quality, research real ITS structure and TPS materials, use SEP's engines, more model detail, a cargo variant; photos at milestones; finish the grid fins; gyros on the ship strong enough to beat aerodynamic forces for a flip and burn; aeroshielding on the legs; a sane polygon count and less lag; fix things floating over the surface; merge with SEP Extras; put it on GitHub; this name. On 2026-11-23 (cloud): a plan and a tool to spend their Claude usage well; the bare-carbon livery to look at; ITS-style windows on SEP's Block 3 nose, the big window on both, a few rows of small windows on the crew nose and one or two on the crew-and-cargo nose.

## Hard rules

1. **Never commit SEP's or Thrimm's files.** SEP's Raptor and Block 3 nosecone are only referenced by path in ModuleManager copies (`its/scripts/make_rings.py`, `v3/scripts/make_nose_cfg.py`); `v3/scripts/layout.py` keeps a few measured radii of the nose, never mesh or texture data.
2. **Part names must not change.** The `default` save has ITS parts in flight, and craft use `SEP.CW.*`.
3. Leave `GameData/SpaceX_ITS` (Thrimm's old mod) on the PC alone; an old craft uses it.
4. No SpaceX endorsement claim. Credit Thrimm and SEP. Our assets are CC BY-NC-SA 4.0, scripts MIT.

## Working in the cloud

```
./tools/cloud_setup.sh          # Blender 3.6.23, io_object_mu + our exporter fix, numpy/Pillow, ImageMagick
source tools/env.sh
./build_all.sh                  # about 2.5 min; ITS_HULL=1024 makes the textures quick for a test
its/p.sh name --view 25,0,60,0,0,87 --sky studio "../Ships/VAB/ITS Crew.craft"     # render -> its/build/photos/name.png
```

`p.sh` works from `its/`, so craft paths start with `../`. Setup, build, a render and the fit check were tested from a clean clone on the PC with no KSP or SEP visible: models came out vertex-identical, textures equal to rounding. First run on a real cloud machine on 2026-11-23: setup, full build (3.5 min), lint, check_fit/float/balance and photos all work. The cloud environment must allow download.blender.org (github.com comes through the git proxy). Ubuntu's ImageMagick is version 6, so setup puts a `magick` shim on PATH via `tools/env.sh`; IM6 ignores `dds:mipmaps=fromlist`, so **cloud DDS have a single mip level**: fine for renders and checks, never ship them (deploy refuses a cloud build anyway). If Blender can't be downloaded, config, patch and script edits are still possible, and `make_cfg.py` needs built models (the release zip has them).

What can't be done in the cloud: run KSP, deploy, read KSP.log, bake the V3 masks, `check_rings.py`, the engine part of `check_fit.py`, and engines in photos (all need SEP). So: **edit, build and check here, push a branch, and the user pulls on the PC** and runs `./build_all.sh && ./deploy.sh` there with KSP closed. A cloud build has no masks and `deploy.sh` refuses it.

`BLENDER`, `IO_OBJECT_MU` and `KSP_DIR` override the PC's paths.

## Layout

| Path | What |
|---|---|
| `build_all.sh`, `deploy.sh` | Build both halves; install on the PC (copies and verifies before removing anything) |
| `tools/` | Cloud setup and the required io_object_mu patch (one submesh per material) |
| `its/scripts/hull.py` | Ship's outer mould line, skirt, paint edge (`paint_d`), texture mapping. Pure numpy, everything uses it |
| `its/scripts/layout.py` | Every shared number: engines, rings, legs, fans, bay, crane, booster, atlas zones |
| `its/scripts/sl.py`, `common.py`, `shell.py`, `fwd.py`, `crane.py` | Geometry library and helpers |
| `its/scripts/build_*.py` | One per part (`./b.sh leg` from `its/`) |
| `its/scripts/tex_*.py`, `tl.py`, `bdb_look.py` | Textures. `bdb_look` is only used to write DDS mips; its look pass is not used |
| `its/scripts/make_cfg.py` | All ITS part configs; node positions come from the built models |
| `its/scripts/make_rings.py` | Engine rings, vacuum Raptor, lite plume (MM patches) |
| `its/scripts/make_craft.py` | `Ships/VAB/*.craft` |
| `its/scripts/photo.py` | Renders a .craft; `--pose ITS_Leg:legDeploy`, `--only`, `--sky day/space/studio`, `--lit` for windows |
| `its/scripts/check_fit.py`, `check_float.py`, `check_balance.py`, `check_rings.py`, `lint.py` | Clearances; pieces touching nothing; TWR and delta-v; engine overlap; cfg/model/texture checks |
| `common/`, `tools/make_icon.py`, `tools/check_cck.py` | CCK part filter (`cck-stms`) and its icons; the check fails the build if a part isn't listed |
| `its/extras/ITS_PBR.cfg.txt` | Opt-in PBR material swap, untested |
| `v3/` | Winch, expendable V3 and the Block 3 crew nosecones' window kits: `build.sh`, `cfg/`, `patches/`, `scripts/` (`nose.py` lays pieces on SEP's nose from the measured rings in `layout.py`) |

## Conventions and traps

- Blender +Z becomes Unity +Y; Unity = (bx, bz, by). Azimuth 0 is Blender -Y, leeward; 180 is windward. Real metres in `hull.py`/`layout.py`, KSP metres = real x 0.625. Ship z = 0 at the vacuum engines' exit, 49.5 at the nose; booster z = 0 at its engines' exit, 77.5 at the top.
- One material per mesh object. Convex colliders of 255 triangles or fewer, marked `separate`. The exporter ignores `matrix_parent_inverse`. KSP culls backfaces, so `facing.py` runs at export.
- `P.empty(name, frame, parent)`: without a parent the empty falls outside the model and is lost. Pass `P.model`.
- **Anything laid on the hull must go through `stick()` or `stick_cyl()`**, which bend it to the curve and sink it 8 mm (the hull is faceted). Flat plates float by up to 11 cm. Run `check_float.py`.
- RCS transforms: local +Z (Unity +Y) is the exhaust. One per cluster of ports, to keep plume counts down.
- Piston servos: KSP overwrites the servo transform's position, so the bone sits at local zero inside an armature object that carries the rest position. Skinned meshes get a zero-area triangle at the far end of travel so Unity doesn't cull them.
- Landing leg follows stock LT-2's layout: leg > wheelCollider, pistonbase > piston > foot, deployTgt.
- The half-hull sheets are mirrored left to right, so no text on them. The booster sheet repeats every 120 degrees; lettering and flag are separate meshes hidden by a B9 switch.
- Texture style (measured from HabTech2 and Orion): calm colour, detail in the gloss channel (1.5-2.8% variation), 85-96% flat normals, clean not weathered, stock `KSP/Bumped Specular`.
- Don't use `pgrep -f KSP...` to test whether KSP runs: it matches its own shell.

## Numbers

- **Balance:** SEP's thrust and Isp (613 kN sea level, 674 kN vacuum per engine), propellant 0.20 of real, dry 0.25. Booster 1,340 t propellant, ~69 t dry with engines. Ship 390 t; dry 37 t crew, 32 t cargo, 22.6 t tanker (500 t propellant). Liftoff TWR ~1.4. LqdMethane:Oxidizer 3:1, B9 tank type `ITSLMOX`.
- **Flip gyros:** ShipAft has an 8,000 kN m reaction wheel (2,500 roll) and 12 EC/s. Estimated aero moment at 3 g entry ~4,400 kN m. Joints are 30,000 so the torque doesn't break the stack. May be twitchy in vacuum: authority limiter.
- **Polygons:** booster 61k triangles (SEP's 229k), aft 37k, crew 29k, cargo 41k, tanker 27k, leg 6k, fan 12k, grid fin 4k. Full cargo stack's own meshes 198k.
- **Lag fix:** the 42 booster Raptors went from 862k triangles / 539 renderers / 126 colliders to 390k / 210 / 15 (`ModuleB9DisableTransform`, `ITS_Ring*Base` colliders). The plume is set to 5 effects per engine instead of 18 (`ITS_Raptor3Lite`).
- **Real vehicle:** carbon-fibre prepreg structure; PICA 3.0 heat shield in large Dragon-style blocks; ship 49.5 x 12 m, 17 m max, 3 SL + 6 vac Raptors; booster 77.5 m, rings 21/14/7, only the center 7 gimbal; stack 122 m (ship's skirt overlaps a cut-away interstage by 5 m). Sources: SpaceX's 2016 slides, its CC0 renders on Wikimedia Commons, Musk's AMA. The cargo ship, array size, thruster sizes and crane are our design.

## Open

**Needs the user, in game:**
1. All three rings fire, with plumes and throttle; center 7 gimbals; booster separates. (Multi-MODEL rings were checked only by reading B9's and Waterfall's code, and that the parts compile.)
2. `ITS_Raptor3Lite` works: in `GameData/ModuleManager.ConfigCache` that template should have exactly 5 `EFFECT` blocks (M1, M3, M4, M5-1, MFO_SL). It had not been through a KSP launch.
3. Lag on the pad, better or not.
4. Legs hold the landed ship (suspension numbers are scaled guesses); foot pitch.
5. The flip against the airstream.
6. Fan arrays deploy and track; crane pistons; side-by-side docking (`dockA`/`dockB`, nodeType ITSTransfer).
7. The save with ITS parts still loads after the merge. `ITS.ShipAft` gained docking and reaction wheel modules and its solar/leg nodes since that craft flew.
8. VAB symmetry on `ITS.ShipAft` (`stackSymmetry = 2`, 16 mixed nodes): with symmetry on, attach one SL Raptor, one vac Raptor, one leg, one fan. If copies land on the wrong nodes, drop `stackSym` in `make_cfg.py`.
9. Whether to turn on PBR. Unknowns: which channel of `_MetalMap` Resurfaced/Standard reads, and whether the hull keeps its painted gloss without one.
10. Block 3 crew nosecones (`STMS_B3_NoseCrew`, `STMS_B3_NoseCrewCargo`; `v3/scripts/build_nosekit.py`, `make_nose_cfg.py`, `check_nose.py`): both appear in the Pods tab with SEP's model plus our windows (two MODELs, like the rings); Toggle Cabin Lights lights only the glass and not SEP's hull (`ModuleColorChanger` with `includedRenderer = stms_b3_glass`, not yet seen working; without it SEP's materials would take the colour too); flaps attach to both fin nodes and, folded or deflected, don't cover the windows (the ITS-style big window's lower corners at 48 deg, z 2.65; small-window edges at 52 deg, z -0.9; hinges at 70 deg, z 4.25); both Ablative subtypes leave the windows on bare steel; RCS still fires; crew board in the VAB and can EVA through the airlock trigger at SEP's hatch (SEP's model has none); the crew-cargo nose sits on SEP's Block 3 cargo section and that bay still shields its payload. Render: `its/build/photos/b3nose_*.png`.

11. Block 3 noses' **Docking door** switch (2026-11-26; `NOSE_DOORS`, `DOCK_C`, `EVA_BAY` in `v3/scripts/layout.py`): an old craft loads with the Side door; switching moves the active node (`port` / `ctrport`, B9 node toggles) and the cargo-bay shielding; on the crew-cargo nose's Centred door, B9's `TRANSFORM positionOffset` really moves `stms_airlock` into the bay, EVA works with the cargo doors open and reports blocked with them shut; the cabin lights still reach the restored windows' glass (a second `stms_b3_glass` under `stms_b3_winS`); with FreeIva, the cabins switch with the door (props `STMS_IVA_Crew*_S/W/C/E`, `B9PSConditionalProp`), the centred door's CBM hatch connects to `ctrport`, and the crew-cargo floor hatch EVAs through the moved airlock. Also the expendable core's windward stringers (`STMS_B3_Stringers`) show with SEP's textures in both Hull subtypes.

**Waiting for a verdict:** bare-carbon livery, an optional B9 switch (Livery: White / Bare carbon, White default) on branch `claude/carbon-livery`; +54 MB of textures, no carbon normal maps. In game: the switch on all five hull parts, switching back, the old save loading, weave shimmer.

**Not built:** a real crew interior (uses `MK3_CrewCab_Int`; FreeIva logs hatch errors for it), RealFuels volumes.

**Known and left alone:** `check_float.py` still lists joint rings, bolts and hinge brackets hidden inside the hull, the lettering (7 mm proud) and the leg shells (they rest on the ship, not on the leg). Fan packages show slightly under the skirt rim when stowed. SEP's own `ModuleSEPRaptor` throws an exception on the SL_C engine in the editor; not ours. `lint.py` warns about `ModuleDeployableAero` (Kerbal Reusability Expansion's DLL isn't scanned).

## Good first steps in a new session

Ask for the user's in-game results and KSP.log excerpts, fix what they report, then the livery verdict, then offer the crew interior.
