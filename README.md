# Starship Thingy Mabobs and Such (STMS)

Add-ons for Kari's [Starship Expansion Project](https://github.com/Kari1407/Starship-Expansion-Project), in one folder: `GameData/StarshipThingyMabobsAndSuch`. 

| | What it adds | Notes |
|---|---|---|
| **V3 ship** | Cargo winch for the V3 cargo bay, and an expendable config for the V3 body | [docs/V3.md](docs/V3.md) |
| **ITS 2016** | The Interplanetary Transport System: booster, engine rings, crew, cargo and tanker ships, legs, solar fans, crane | [docs/ITS.md](docs/ITS.md) |

## Install

Download the zip from Releases and copy its `GameData/StarshipThingyMabobsAndSuch` into `GameData`. Delete `GameData/SEPExtras` and `GameData/StarshipITS` if you have them: their parts now live here under the same names, so saves and craft keep working. Craft files are in `Ships/VAB`.

Needs SEP, ModuleManager and B9PartSwitch. The winch and crane need Breaking Ground.

## Build

`./build_all.sh` builds both halves (Blender 3.6 with io_object_mu; Python with numpy and Pillow; SEP installed, for the V3 masks). `SKIP_MODELS=1` and `SKIP_TEX=1` reuse the last build. `./deploy.sh` copies it into the Sol install.

## Licence

See [LICENSE](LICENSE). The V3 mask textures in the release are derived from SEP's, which are All Rights Reserved, and the engine rings show SEP's engines. Don't make this repository or its releases public without Kari's permission.
