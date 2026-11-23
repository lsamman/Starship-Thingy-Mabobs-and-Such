# Starship HLS

Four parts and a craft file (`Ships/VAB/Starship HLS.craft`), modelled on the NASA/SpaceX renders of November 2024, reissued by SpaceX in October 2025 and still the latest published in August 2026. SEP's size (5.625 m hull), all our own geometry and textures. Needs SEP (for the Raptors), B9PartSwitch, and Breaking Ground for the elevator.

| Part | What it does |
|---|---|
| **Core** (`STMS_HLS_Core`) | 322 t of methalox, 3 sea-level + 3 vacuum Raptor 3 nodes, 18 landing thrusters in the black band, 4 leg nodes, elevator track and ladder, RCS, floodlights |
| **Crew Section** (`STMS_HLS_Crew`) | 8 crew, ten windows, airlock bay with an awning door, two solar arrays behind the side hatches, nose cap over a docking port |
| **Landing Leg** (`STMS_HLS_Leg`) | Use four |
| **Elevator** (`STMS_HLS_Lift`) | Goes on the `lift` node in the airlock; a Breaking Ground piston, 22.3 m |

## SEP compatibility

- Engines are SEP's own `SEP_26_R3_SL_C` and `SEP_26_R3_VAC`, at the positions SEP's Block 3 ship uses.
- The core's bottom fits SEP's Block 3 booster; the joint between core and crew section sits where SEP's does, so SEP's Block 3 noses go on this core and this crew section goes on SEP's core.
- SEP's ship-to-ship docking hardware fits the `docking` node on the far side from the door. It is 3.25 m higher than on SEP's ship, so its aft latches clear the stowed legs. A docked tanker sits that much further forward.
- The nose port takes Benjee10's NDS/APAS ports (Orion) and stock standard ports. Open the nose cap first.

## Landing

Dry about 45 t with engines and gear. The ring gives 540 kN, 414 kN of it straight down, so it can hover up to 255 t in lunar gravity. Brake with the Raptors, shut them down near the ground (about 100 m), activate the landing thrusters on the core. They share the throttle.

On the ground: Open Airlock Door, Lower Deck, then slide the elevator's Target Extension to -22.3. Back to 0, fold the deck and close the door before leaving. The track is also a ladder.

## Where it differs from the renders

- No NASA or SpaceX logos; a flag on the door (switchable).
- The renders show no solar arrays, only outlined hatches; the roll-out arrays are our reading of those.
- Press describes a dozen landing engines; the renders space them for six groups of three, so 18.
- The band sits about a metre lower (real scale), to stay on the core's side of SEP's joint. The track is recessed deeper, so the folded elevator fits behind the door. Crew interior is the stock Mk3 cabin.
