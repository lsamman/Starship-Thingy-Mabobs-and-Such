# Starship HLS

The parts and a craft file (`Ships/VAB/Starship HLS.craft`), modelled on the NASA/SpaceX renders of November 2024, reissued by SpaceX in October 2025 and still the latest published in August 2026. SEP's size (5.625 m hull), all our own geometry and textures. Needs SEP (for the Raptors), B9PartSwitch, and Breaking Ground for the elevator.

| Part | What it does |
|---|---|
| **Core** (`STMS_HLS_Core`) | 322 t of methalox, 3 sea-level + 3 vacuum Raptor 3 nodes, 18 landing thrusters in the black band, 4 leg nodes, elevator rails and ladder on the hull (a switch), RCS, floodlights |
| **Crew Section** (`STMS_HLS_Crew`) | 8 crew, ten windows, airlock bay with an awning door, five solar bays, nose cap over a flat seat for a docking port (shielded while shut) |
| **Crew Section, Tall Cabin** (`STMS_HLS_CrewTall`) | The same nose with seven rows of windows and five decks: 16 crew, observation lounge, bunks, galley, flight deck, airlock. Same airlock, door, solar bays and both elevators |
| **Solar Array** (`STMS_HLS_Solar`) | One per solar bay, five in all |
| **Leg Shroud** (`STMS_HLS_LegShroud`) | Jettisonable, one over each folded leg |
| **Docking Hardware** (`STMS_HLS_Docking_M`, `_F`) | SEP's ship-to-ship docking parts in white, for the node on the far side of the core |
| **Landing Leg** (`STMS_HLS_Leg`) | Use four |
| **Elevator** (`STMS_HLS_Lift`) | Goes on the `lift` node in the airlock; a Breaking Ground piston, 22.3 m |

## Two elevators

**Elevator** rides the rails on the hull. **Elevator (Cable)** (`STMS_HLS_LiftCable`), after the NASA/SpaceX render, is an open cage on four cables: it goes on the same `lift` node, and the **Elevator track** switches on the core and the crew section go to None. Run Cage Out, then Target Extension -22.3. Without the rails there is no ladder either.

## Two styles

The core and crew section have a **Style** switch: **Original** (black base, leg panels, tall band; the default, so saved ships keep their look) and **2024 render** (all white, thin band, faired legs, after SpaceX's cargo lander render). Both have a solid tank wall with the rails and ladder outside it. Use **Landing Leg** with the original, **Landing Leg (Faired)** with the 2024 render. The jettisonable shrouds belong to the original; **Leg Pod Cover** closes the pods of the 2024 render, on the same nodes, and is jettisoned before the leg comes down.

## Cargo versions

- **Cargo Section (Bay Doors)** (`STMS_HLS_Cargo`): SEP's Block 3 cargo section in white. Winch boom on the ceiling node; the platform reaches the ground at about -25.7.
- **Cargo Section (Awning Door)** (`STMS_HLS_CargoAwning`): our own, one wide door that swings up. Put the **Crane Frame** (`STMS_HLS_Crane`) on the node by the sill and the Cargo Winch Hoist on the node under its crossbar; open the door, slide the frame's Target Extension to -4.4, then lower the hoist (ground at about -23.5). Or set **Boom mount** to Beams and use the winch boom on its node instead; not both. The bay is open up to the header tank, about 7 m over the floor. Set the core's **Elevator track** to None.

The door and the crane frame guard each other: the door will not close while the frame is out, and the frame will not run out until the door is fully open.

## Several loads in one ship

Awning-door cargo section with the crane frame, hoist and platform. Load 1 rides on the platform. **Cargo Floor (Mid)** goes on node `floor1` and carries load 2 over the stowed crane: up to about 2.2 m tall, or 1.3 m with a **Cargo Floor (Top)** on `floor2`, which takes a flat load 3 up to 0.8 m tall. Widths up to about 1.9 m (2.6 m on the platform), lengths about 2.9 m. Keep loads 2 and 3 on a decoupler or docking port until their floor is down.

1. Open the door, crane to -4.4, lower load 1, let it go, bring the hoist back up. **Leave the crane out.**
2. Put Ramp Out (folded, it blocks the floor). Set the hoist to -1.7: the platform is just under the ramp's tip.
3. Mid floor to -4.45. Free load 2, drive it over the ramp onto the platform, brake. Fold Ramp In is not needed; lower the hoist.
4. Hoist back to -1.7, Top floor to -5.74: it lands on the Mid floor and has a sloped edge. Same again.

Loads without wheels: put a **Cargo Tray** on the floor's node with the load decoupled from its carriage node. Floor down, hoist at -1.8, tray to -4.1, decouple, tray back to 0.

## Solar arrays

Five bays, one at the back (az 180, node `solar5`) as well as the four on the sides; ships saved with four keep theirs. Each bay is a shallow pocket (0.32 m) with eight thin panels folded flat in it. Extending opens the hatch, runs the carriage 0.25 m out, folds the array out from its hinge at the bay's foot, then telescopes it to about 8 m.

Each array has **Lock Tracking** and **Rotate Array Down** (right-click, or action groups), from the small plugin in `its/plugin`. Rotating down turns tracking off, centres the array and hangs it along the hull; it stays locked until it is out again, and Retract raises it first. Hanging, it passes over the landing thrusters, so do it after landing.

## SEP compatibility

- Engines are SEP's own `SEP_26_R3_SL_C` and `SEP_26_R3_VAC`, at the positions SEP's Block 3 ship uses.
- The core's bottom fits SEP's Block 3 booster; the joint between core and crew section sits where SEP's does, so SEP's Block 3 noses go on this core and this crew section goes on SEP's core.
- SEP's ship-to-ship docking hardware fits the `docking` node on the far side from the door, at the same height as on SEP's Block 3 ship, so a docked tanker lines up as it would with SEP's.
- The nose seat takes any docking port, for instance Benjee10's NDS for Orion. Open the nose cap first.

## Landing

Dry about 45 t with engines and gear. The ring gives 540 kN, 414 kN of it straight down, so it can hover up to 255 t in lunar gravity. Brake with the Raptors, shut them down near the ground (about 100 m), activate the landing thrusters on the core. They share the throttle.

On the ground: Open Airlock Door, Lower Deck, then slide the elevator's Target Extension to -22.3. Back to 0, fold the deck and close the door before leaving. The track is also a ladder.

## Where it differs from the renders

- No NASA or SpaceX logos; a flag on the door (switchable).
- The lunar-surface render shows the arrays stowed flat on the hull and the orbit render shows them deployed; the fold-out, roll-out mechanism is our reading of those.
- Press describes a dozen landing engines; the renders space them for six groups of three, so 18.
- The band sits about a metre lower (real scale), to stay on the core's side of SEP's joint. The elevator is stowed inside the airlock; Lower Deck slides it out over the sill onto the rails first.

## Interiors

`its/scripts/ivalib.py` builds four cabins from `iva_layout.py`: HLS (one tall main deck under the dome with a cockpit mezzanine, lockers, wood counters and a table, airlock deck below, after SpaceX's October 2025 renders), HLS Tall (lounge, bunks, galley, flight deck, airlock), and the Block 3 crew and crew-cargo noses. White panelled rooms with cove lighting, a curved console under the windows and a ladder well, after SpaceX's October 2025 cabin renders. Seats, displays, lockers and galley are HabTechProps and stock props, by name, so **HabTechProps must be installed** or those are missing (KSP logs it; the room and the crew positions still work). Double-click a window to look out. FreeIva works: unbuckle, climb the ladder, leave by the airlock or the docking hatch. Render: `its/ri.sh name STMS_IVA_HLS x,y,z,tx,ty,tz`.

## Other parts made alongside

- **Block 3 Landing Leg** (`STMS_Ship_Leg`): the HLS leg in the ship's bare steel, no shell. Four nodes are added to SEP's Block 3 core; it also surface-attaches.
- **Ship Quick Disconnect Arm** goes on the free rear node of SLE's own tower core, and **Crew Access Arm** attaches radially beside the rear column (azimuth -37 face, the collider is one square box), floor level with the EVA hatch sill. Both reach round the chopstick carriage and swing back clear of it. No extra tower part is needed.
- **Crew Access Arm** and **Ship Quick Disconnect Arm**: for those nodes. Heights and reach fit a SEP Block 3 stack on SLE's table with the ship's window side to the tower (`its/scripts/tower_layout.py`). The white room meets the EVA hatch of both crew noses; the other arm meets SEP's QD plate, holds the booster with a claw, and can load propellant. With StagedAnimation installed it retracts when staged: jaws open, plate and claw pull back, then it swings about 130 degrees, 3.5 s in all. `its/scripts/check_arms.py` runs both retractions against booster, ship and nose. They share the tower's sides with SLE's chopsticks, whose carriage passes through them if driven past.

## Avionics cockpit

With **FreeIva**, **RasterPropMonitor** (1.1 or later) and **ASET Props** and **ASET Avionics** installed, the HLS crew sections and the Block 3 crew noses get a **Cockpit** switch: **Classic** (the default, as before) or **Avionics**, an interactive cockpit after ASET's ALCOR. Its props are ASET's, placed by name; `its/scripts/avionics.py` lists the panels and which station carries them, and `its/data/aset_mounts.json` says how each prop sits on a panel (from ALCOR's cockpit; rebuilt by `its/scripts/aset_mounts.py` from an install with ALCOR).

Each flight deck has four stations, left to right from the seats; each has panels on the desk and on a board below it (on the HLS, a console on a pedestal before each seat):

No window looks along the ship, so the pilot's first display is a **landing camera monitor** (ALCOR's landing page, with altitude and vertical speed, over the hull cameras below) and the commander's is a **docking camera monitor** (the docking port you control from); both are copies of ASET's 40x20 display made at load (`its/patches/STMS_CamMonitors.cfg`).

1. 60x30 multifunction display; caution and warning lights with the terrain, slope, tumble and G warnings and the altitude alarm; gear, brakes, parachutes and lights; docking indicators.
2. Two 40x20 displays; SAS on and all its modes, its speed selector, RCS, precision input, gimbal lock, clear target and node; staging (with its lock), guarded abort and undock, engines, engine mode, thrust limiter, throttle cut and full; rotation, translation and throttle hand controllers.
3. Two 40x20 displays; MechJeb: SmartASS modes and roll holds, the manoeuvre planner (Hohmann, circularise, change Ap and Pe, launch inclination and altitude, from the number input below), autopilots for ascent, rendezvous, docking and landing, execute node; comms (CommNet, Chatterer); action groups 1-10 and time warp.
4. A 40x20 display; propellant, thrust, heat and Δv gauges and readouts; environment readouts; power (solar arrays, fuel cells, generators, output selector).

The displays carry ALCOR's pages: flight display, orbit, landing and ascent with a camera, docking camera (from the docking port set as reference), target menu, the hull cameras (ExtCam1-3: down along the hull for landing, outward, up along the nose; renumber them in the part menu if a ship has several), flight log, crew, science, resources, and MechJeb's, SCANsat's and VesselView's pages where those are installed. Light buttons switch the flood lights over the panels and the deck lights. ASET's props add about 66 MB of textures; the displays render only while you are in IVA.

## Hull cameras

With RasterPropMonitor or Hullcam VDS, the ships carry cameras for the displays' camera pages (and Hullcam's camera list), placed after the ship views of SpaceX's flight livestreams, with fixed numbers so a page always means the same view (renumber in the part menu if a ship carries two of a kind):

| | SEP's Block 3 ship (core and nose) | HLS (core and crew section) |
|---|---|---|
| ExtCam1 | aft, down past the engines: SEP's engine bay camera | landing: low on the hull, down past the legs |
| ExtCam2 | engine bay: SEP's camera | engine bay |
| ExtCam3, 4 | aft flaps: SEP's cameras | a leg and its footpad; the docking hardware |
| ExtCam5, 6 | forward flaps: SEP's cameras | airlock and elevator, down the hull; horizon |
| ExtCam7 | cargo and Pez: SEP's payload bay camera by the door | hull looking aft |
| ExtCam8 | cargo and Pez: SEP's payload bay camera from above | nose looking forward |

On SEP's ship these are all SEP's own cameras: RasterPropMonitor uses SEP's transforms, Hullcam keeps SEP's modules (the crew noses keep SEP's flap cameras too), and nothing of ours is added to SEP's parts. The patch is `its/patches/STMS_Cameras.cfg`, written by `its/scripts/make_cameras_cfg.py`; the HLS's cameras are in its own models. On the HLS, **Camera pods: Shown / Hidden** hides the pods on the outside; the cameras keep working.

## Life support

With TAC Life Support, Snacks or USI Life Support, the four crew cabins carry supplies at the ITS crew section's rate per kerbal (`its/patches/STMS_LifeSupport.cfg`); Kerbalism equips crewed parts itself.

