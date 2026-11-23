# ITS 2016

The 2016 Interplanetary Transport System for KSP 1.12, rebuilt from scratch at Starship Expansion Project scale (0.625 of real size, 7.5 m body). Continues the idea of Thrimm's 2016 *SpaceX ITS* mod; none of its models or textures are used here.

## Needs

- [Starship Expansion Project](https://github.com/Kari1407/Starship-Expansion-Project) (the Raptor 3 engines, referenced from your own install; nothing of SEP's is included)
- ModuleManager, B9PartSwitch, Community Resource Pack
- Breaking Ground, for the cargo crane only
- Optional: Waterfall (plumes), Kerbal Reusability Expansion (grid fins stop steering while stowed)

## Parts

| Part | Notes |
|---|---|
| Booster | 1,340 t of methalox, interstage, decoupler, probe core. Nodes for three engine rings and three grid fins |
| Raptor rings 21, 14, 7 | 42 of SEP's Raptor 3; the center seven gimbal 7 degrees |
| Grid Fin | Hinged; Brakes group deploys it |
| Ship Aft Section | 390 t, nodes for 3 sea-level and 6 vacuum Raptors, 3 legs, 2 arrays. Holds the flip gyros (8 MN m) and two propellant transfer ports |
| Crew / Cargo / Tanker Section | 16 crew; clamshell bay with crane mount; 110 t more propellant |
| Vacuum Raptor | SEP's, at 1.35x |
| Landing Leg, Fan Solar Array | |
| Cargo crane | Boom, hoist and platform |

Ready-made craft are in `Ships/VAB`.

## Flying it

- **Entry:** black side to the wind. The gyros can hold the ship broadside and swing it upright against the airstream for the landing burn; turn the reaction wheel's authority down if it feels twitchy in space.
- **Refuelling:** bring two ships side by side, bellies outward, and dock the transfer ports on the flank above the skirt.
- **Crane:** doors open, boom to -6.8, then lower the hoist. Keep autostrut off on the crane and its cargo. The platform comes down beside the leeward foot.
- **Solar fans:** they stow inside the skirt. Don't open them with the engines running.

## PBR materials (untested)

`StarshipThingyMabobsAndSuch/ITS/Extras/ITS_PBR.cfg.txt` swaps the hull to Resurfaced's PBR shader so it matches SEP's engines. It needs Shabby and Resurfaced and has not been judged in game. Rename it to `ITS_PBR.cfg` to try it, and back to compare.

## What is documented and what is not

From SpaceX's 2016 presentation and renders: sizes, masses, engine counts, carbon-fibre structure, PICA heat shield, window layout, legs, fan arrays, hexagonal grid fins. Invented: the cargo section (SpaceX never showed one), thruster sizes, solar array size, the crane. Thrust is SEP's quarter scale, propellant a fifth and dry mass a quarter of the real figures.

## Checks

`its/scripts`: `lint.py`, `check_rings.py`, `check_fit.py`, `check_float.py`, `check_balance.py`.

## Credits and licence

Original mod: Thrimm. Raptor engines: Kari and the SEP team, All Rights Reserved, used in place from your SEP install. Models, textures and configs here: lsamman, CC BY-NC-SA 4.0. Scripts: MIT. Not affiliated with or endorsed by SpaceX.
