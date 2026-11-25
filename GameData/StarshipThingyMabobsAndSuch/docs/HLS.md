# Starship HLS

The parts and a craft file (`Ships/VAB/Starship HLS.craft`), modelled on the NASA/SpaceX renders of November 2024, reissued by SpaceX in October 2025 and still the latest published in August 2026. SEP's size (5.625 m hull), all our own geometry and textures. Needs SEP (for the Raptors), B9PartSwitch, and Breaking Ground for the elevator.

| Part | What it does |
|---|---|
| **Core** (`STMS_HLS_Core`) | 322 t of methalox, 3 sea-level + 3 vacuum Raptor 3 nodes, 18 landing thrusters in the black band, 4 leg nodes, elevator rails and ladder on the hull (a switch), RCS, floodlights |
| **Crew Section** (`STMS_HLS_Crew`) | 8 crew, ten windows, airlock bay with an awning door, four solar bays, nose cap over a flat seat for a docking port (shielded while shut) |
| **Solar Array** (`STMS_HLS_Solar`) | One per solar bay, four in all |
| **Leg Shroud** (`STMS_HLS_LegShroud`) | Jettisonable, one over each folded leg |
| **Docking Hardware** (`STMS_HLS_Docking_M`, `_F`) | SEP's ship-to-ship docking parts in white, for the node on the far side of the core |
| **Landing Leg** (`STMS_HLS_Leg`) | Use four |
| **Elevator** (`STMS_HLS_Lift`) | Goes on the `lift` node in the airlock; a Breaking Ground piston, 22.3 m |

## Two styles

The core and crew section have a **Style** switch: **Original** (black base, leg panels, tall band; the default, so saved ships keep their look) and **2024 render** (all white, thin band, faired legs, after SpaceX's cargo lander render). Both have a solid tank wall with the rails and ladder outside it. Use **Landing Leg** with the original, **Landing Leg (Faired)** with the 2024 render. The jettisonable shrouds belong to the original.

## Cargo versions

- **Cargo Section (Bay Doors)** (`STMS_HLS_Cargo`): SEP's Block 3 cargo section in white. Winch boom on the ceiling node; the platform reaches the ground at about -25.7.
- **Cargo Section (Awning Door)** (`STMS_HLS_CargoAwning`): our own, one wide door that swings up. Put the **Crane Frame** (`STMS_HLS_Crane`) on the node by the sill and the Cargo Winch Hoist on the node under its crossbar; open the door, slide the frame's Target Extension to -4.4, then lower the hoist (ground at about -23.5). Or use the winch boom on the ceiling node instead; not both. Set the core's **Elevator track** to None.

## Solar arrays

Each array has **Lock Tracking** and **Rotate Array Down** (right-click, or action groups), from the small plugin in `its/plugin`. Rotating down turns tracking off, centres the array and hangs it along the hull; it stays locked until it is out again, and Retract raises it first. Hanging, it passes over the landing thrusters, so do it after landing.

## SEP compatibility

- Engines are SEP's own `SEP_26_R3_SL_C` and `SEP_26_R3_VAC`, at the positions SEP's Block 3 ship uses.
- The core's bottom fits SEP's Block 3 booster; the joint between core and crew section sits where SEP's does, so SEP's Block 3 noses go on this core and this crew section goes on SEP's core.
- SEP's ship-to-ship docking hardware fits the `docking` node on the far side from the door. It is 3.25 m higher than on SEP's ship, so its aft latches clear the stowed legs. A docked tanker sits that much further forward.
- The nose seat takes any docking port, for instance Benjee10's NDS for Orion. Open the nose cap first.

## Landing

Dry about 45 t with engines and gear. The ring gives 540 kN, 414 kN of it straight down, so it can hover up to 255 t in lunar gravity. Brake with the Raptors, shut them down near the ground (about 100 m), activate the landing thrusters on the core. They share the throttle.

On the ground: Open Airlock Door, Lower Deck, then slide the elevator's Target Extension to -22.3. Back to 0, fold the deck and close the door before leaving. The track is also a ladder.

## Where it differs from the renders

- No NASA or SpaceX logos; a flag on the door (switchable).
- The renders show no solar arrays, only outlined hatches; the roll-out arrays are our reading of those.
- Press describes a dozen landing engines; the renders space them for six groups of three, so 18.
- The band sits about a metre lower (real scale), to stay on the core's side of SEP's joint. The elevator is stowed inside the airlock; Lower Deck slides it out over the sill onto the rails first.

## Interiors

`its/scripts/ivalib.py` builds three cabins from `iva_layout.py`: HLS (flight deck and wardroom, airlock deck below), and the Block 3 crew and crew-cargo noses. White panelled rooms with cove lighting, a curved console under the windows and a ladder well, after SpaceX's October 2025 cabin renders. Seats, displays, lockers and galley are HabTechProps and stock props, by name, so **HabTechProps must be installed** or those are missing (KSP logs it; the room and the crew positions still work). Double-click a window to look out. FreeIva works: unbuckle, climb the ladder, leave by the airlock or the docking hatch. Render: `its/ri.sh name STMS_IVA_HLS x,y,z,tx,ty,tz`.

## Other parts made alongside

- **Block 3 Landing Leg, aeroshielded** (`STMS_Ship_Leg`): the HLS leg under a shell that rides out with it, steel or tiles. Four nodes are added to SEP's Block 3 core; it also surface-attaches.
- **Ship Quick Disconnect Arm** goes on the free rear node of SLE's own tower core, and **Crew Access Arm** attaches radially beside the rear column (azimuth -37 face, the collider is one square box), floor level with the EVA hatch sill. Both reach round the chopstick carriage and swing back clear of it. No extra tower part is needed.
- **Crew Access Arm** and **Ship Quick Disconnect Arm**: for those nodes. Heights and reach fit a SEP Block 3 stack on SLE's table with the ship's window side to the tower (`its/scripts/tower_layout.py`). The white room meets the EVA hatch of both crew noses; the other arm meets SEP's QD plate, holds the booster with a claw, and can load propellant. With StagedAnimation installed it retracts when staged: jaws open, plate and claw pull back, then it swings about 130 degrees, 3.5 s in all. `its/scripts/check_arms.py` runs both retractions against booster, ship and nose. They share the tower's sides with SLE's chopsticks, whose carriage passes through them if driven past.
