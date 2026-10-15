# Free 3D model libraries

Sources: ahujasid/blender-mcp source (`server.py` `search_assets` / `import_asset`, `addon.py` Poly Haven / Poly Pizza / Sketchfab handlers), read 2026-10-08. Licence texts: creativecommons.org. The per-site notes on accounts and keys come from the addon code. Check each site's current terms before shipping.

## The three sources the `blender` MCP already knows

| | Poly Haven | Poly Pizza | Sketchfab |
|---|---|---|---|
| what | realistic models, PBR textures, HDRIs | stylised low-poly models | huge user catalogue, realistic and specific items |
| licence | **all CC0** (no credit needed) | **CC0 or CC-BY** per model | varies per model (see below) |
| account / key | none | free API key (addon setting "Poly Pizza API key") | free account + API token (addon setting "Sketchfab API Key"); only "downloadable" models |
| good for FiveM | furniture, crates, plants, food, tools; realistic but often high-poly | cheap props, signs, toys; may look cartoonish next to GTA | specific objects ("ATM", "vending machine", "barber chair") |
| `search_assets` | `source="polyhaven"`, `asset_type="models"`, `previews=3` | `source="polypizza"`, `licence="CC0"` | `source="sketchfab"`, `query=…`, `previews=3` |

Then `import_asset(source=…, id=…)`. The MCP reports the model's licence and author, and for Poly Pizza writes the attribution onto the object. Copy it into `CREDITS.md`.

The Poly Pizza CDN sits behind Cloudflare. If an import fails with a bot-protection error, download the `.glb` by hand from poly.pizza and import it (the addon says the same).

Other free sources the MCP doesn't search (download by hand): **Kenney** (kenney.nl, CC0 low-poly packs), **ambientCG** (CC0 PBR textures, good for retexturing generated models), **Poly Haven textures** for Sollumz materials.

## Licences you'll meet on Sketchfab

| Licence | OK for a FiveM server resource? |
|---|---|
| CC0 | yes, no conditions |
| CC BY | yes, **credit the author** (CREDITS.md, and the in-game credits/Discord if you publish) |
| CC BY-SA | yes, with credit; edited versions must use the same licence. A problem only if you sell or encrypt (escrow) the resource |
| CC BY-ND | **no**: converting, decimating and retexturing count as changing it |
| CC BY-NC / NC-SA / NC-ND | **avoid** if the server takes donations, sells VIP or runs a Tebex shop; "non-commercial" is unclear there. NC-ND also forbids changes |
| Standard / Editorial (Sketchfab Store) | paid store licences. Don't buy (project rule) |

Not legal advice. When in doubt, pick CC0.

## Red flags: skip these models

- **Ripped game assets** ("GTA V ripped", "from Cyberpunk", "Call of Duty model"). A CC licence on Sketchfab doesn't make them legal. Rockstar's own models are already in the game; use the vanilla prop (muto-atlas `/prop`) instead.
- Branded products and logos (Coca-Cola can, Nike shoe) for a public resource. Retexture without the logo.
- Uploads with no author history that look professionally made: often re-uploads of paid assets.
- Huge files (hundreds of thousands of faces, 8K textures). Usable only after heavy reduction (`to-gta.md`).

## CREDITS.md template

```markdown
# Credits

| Asset | File | Source | Author | Licence | Changes |
|---|---|---|---|---|---|
| Wooden crate | prop_dio_crate.ydr | https://polyhaven.com/a/wooden_crate_01 | Poly Haven | CC0 | decimated, LODs, Sollumz |
| Burger | prop_dio_burger.ydr | generated locally from burger.png | Hunyuan3D-2.1 (Tencent) | Tencent Hunyuan 3D 2.1 Community License | decimated, retextured |
```
Keep it inside the resource folder, and keep the original download (zip/glb) in a separate `source/` folder outside `stream/`.
