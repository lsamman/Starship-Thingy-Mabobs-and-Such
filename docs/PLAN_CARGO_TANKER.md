> Plan B (tanker nose) was dropped on 2026-11-25: the depot, `STMS_B3_Depot`, is what was wanted.

# Draft plans: HLS Cargo and Block 3 Tanker

Draft of 24 Nov 2026, nothing built. SEP scale (real x 0.625, mass x 0.244). 1 tank unit of methalox = 3.92 kg, so SEP's 82,000-unit core is 322 t.

Rules for both: SEP meshes and textures stay in the player's SEP install (referenced by path, or cut locally and git-ignored). Textures come from
SEP's or STMS's existing sheets; at most one new 1k sheet a ship, because the install is already over its VRAM.

## A. HLS Cargo

**What it is.** The uncrewed lander: STMS's HLS core and legs under a cargo section with a door and a winch. NASA's target for the real one is
12-15 t landed, about 3-3.7 t at this scale. Design point here: **15 t**, so SEP-scale rovers and bases fit.

| Piece | Source | Work |
|---|---|---|
| Core, legs, shrouds, docking hardware, solar | STMS_HLS_* | Reuse as they are |
| **Cargo section** `STMS_HLS_Cargo` | Copy of SEP_26_SHIP_CARGO: no tiles, ablative, flap nodes; white | New config + white masks |
| Winch | SEP_CW boom, hoist, platform | Reuse; lands on the bay's existing `winch` node |
| Probe core, lights, RCS, antenna | Config, as the HLS crew section has | New config |
| Solar | STMS_HLS_Solar needs its bays; put arrays on new surface mounts | New mount, small model |

**Fit (calculated from layout.py and hls_layout.py, to be checked by script):**
- The bay floor sits about 0.4 m above the core's top, 22.5 m above the pads (soles at -1.0).
- Deck from stowed to ground is about 25.7 m; the hoist reaches 29.1 m.
- Boom out, the deck's back edge is at y = -3.4, outside the hull (2.81). It passes between the two door-side feet (x +-3.8, y -3.8; deck +-1.6 wide).
- The elevator track is on the same side (azimuth 0). Clear while the platform is out, but a cargo ship needs no elevator.

**Steps**
1. Config copy, and strip flaps, tiles, ablative (STMS_B3_Expendable.cfg is the model).
2. White hull masks and paint for SEP's cargo mesh through B9 (`bake_masks.py`), matched to the HLS core's white.
3. `check_hls.py`: winch path against core, legs, band; bay against a 2.4 m wide cargo.
4. Delta-v and hover check. First estimate: dry 45 t + 15 t cargo, 322 t propellant, Isp about 375 s: **about 6.8 km/s**. The landing ring hovers 255 t in lunar gravity, enough.
5. Craft file, IVA none, docs, CCK list.

**Main risk:** SEP's mesh in white may look patchy where tiles covered it (its AO is black there; the expendable core needed baked masks).
**Fallback:** our own cargo section on the HLS crew shell, with one big awning door. Looks closer to HLS, 2-3 times the work.

## B. Block 3 Tanker

**What it is.** SEP's reusable core with a closed, windowless nose that carries propellant, and docking hardware to deliver it. It flies home, so tiles and flaps stay.

| Piece | Source | Work |
|---|---|---|
| Core, flaps, engines | SEP_26_* | Reuse |
| **Tanker nose** `STMS_B3_TankerNose` | Copy of SEP_26_SHIP_NOSECONE, interior hidden | Config + small model |
| Fill and vent panel, conduit run, forward RCS | STMS (FwdRCS option exists) | Small model |
| Docking hardware | SEP active and passive | Reuse: tanker active, HLS passive (same transfer node) |

**Capacity.** The nose shell holds about 184 m3 (measured for the crew noses). Estimated useful tank **24,000 units (94 t)**, plus SEP's 82,000. But a full
extra tank is more than the stack can lift: the propellant it *delivers* is limited by payload, roughly **25-30 t** per flight at SEP's scale. So:
- Default fill: 7,500 units (29 t) in the nose, the rest empty, adjustable in the editor.
- An HLS core needs about **11-13 tanker flights** to fill from empty; fewer if it keeps propellant from ascent. (322 t / 25-30 t.)

**Steps**
1. Config copy: tank volume, dry mass (9 t, less interior, plus tank: about 10 t), no crew, probe control, Forward RCS on by default.
2. Hide the crew interior meshes; check nothing shows through the hull.
3. Model: vent and fill panel, conduit, end caps as on STMS_RacewayCap; SEP steel through B9 (never MODEL `texture =`).
4. Propellant settling: aft RCS is SEP's; check it can hold 0.001 g on a 350 t stack.
5. Boil-off: SEP's tanks boil off (ModuleCryoTank, BoiloffRate 0.005; check its unit); **STMS_HLS_Core loses none**. Copy SEP's ModuleCryoTank setup to it, or leave it out on purpose.
6. `check_docking.py`: tanker and HLS docked back to back, flaps and legs clear; the HLS hardware is 3.25 m higher than SEP's.
7. Craft file: tanker, and a docked HLS + tanker test craft.

**Main risk:** docking alignment. SEP's capture range is 0.2 m, and flaps and HLS legs are close to each other. Check geometry before modelling.

**Option C, later: depot.** White HLS core without landing engines or legs, tanker nose, sunshade and radiators. Cheap once A and B exist.

## Order

1. B step 6 and A step 3: geometry checks, no art. They decide whether either plan changes.
2. A as a config-only version, for a look in game.
3. B as a config-only version, for a docked transfer in game.
4. Art: white masks (A), panel and conduit (B).
5. Depot, if wanted.

## To decide

1. HLS Cargo: SEP's bay in white (quick), or our own cargo section (closer to HLS)?
2. Tanker: 24,000-unit nose with a 7,500 default, or fix it at what it can lift?
3. Boil-off on STMS_HLS_Core: yes or no?
4. Depot: now, later, or never?
