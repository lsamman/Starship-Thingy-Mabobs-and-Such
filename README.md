# Starship Thingy Mabobs and Such (STMS)

**I take no credit for anything in this mod, this is based off of other modders hard work and you should check out their stuff**

BDB devs

Benjee10

SEP devs

Modders Bible

Add-ons for Kari's [Starship Expansion Project](https://github.com/Kari1407/Starship-Expansion-Project), in one folder: `GameData/StarshipThingyMabobsAndSuch`. 

| | What it adds | Notes |
|---|---|---|
| **V3 ship** | Cargo winch for the V3 cargo bay, an expendable config for the V3 body, and two crew nosecones with ITS-style windows | [docs/V3.md](docs/V3.md) |
| **ITS 2016** | The Interplanetary Transport System: booster, engine rings, crew, cargo and tanker ships, legs, solar fans, crane | [docs/ITS.md](docs/ITS.md) |
| **Starship HLS** | The lunar lander on SEP's Raptors: core, crew section, legs, elevator | [docs/HLS.md](docs/HLS.md) |

## Install

Download the zip from Releases and copy its `GameData/StarshipThingyMabobsAndSuch` into `GameData`. Delete `GameData/SEPExtras` and `GameData/StarshipITS` if you have them: their parts now live here under the same names, so saves and craft keep working. Craft files are in `Ships/VAB`.

Needs SEP, ModuleManager and B9PartSwitch. The winch and crane need Breaking Ground.

With Community Category Kit installed, all parts are also under **Starship Thingy Mabobs** in the editor's Filter by Function list.

## Build

`./build_all.sh` builds both halves (Blender 3.6 with io_object_mu; Python with numpy and Pillow; SEP installed, for the V3 masks). `SKIP_MODELS=1` and `SKIP_TEX=1` reuse the last build. `./deploy.sh` copies it into the Sol install.

## Licence

See [LICENSE](LICENSE). The V3 mask textures in the release are derived from SEP's, which are All Rights Reserved, and the engine rings show SEP's engines.
