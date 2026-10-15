# Asset integration

## Visual asset and collision

Inspect the exported hierarchy rather than object names alone. Sollumz conversion assigns a mesh to a LOD; it does not generate every reduced mesh. Compare intended LODs after fresh import.

Blender-only nodes do not establish exported game shader behavior. Inspect normals, UVs, texture references and backface culling. Determine embedded versus external textures from the selected asset path; absence of a separate YTD is not automatically an error.

Choose embedded bounds versus an external YBN deliberately. Inspect transforms, collision extent, surface assignments and flags in a game-aware viewer. Keep collision simple enough for its purpose while preserving steps, passages and player/vehicle clearance. A mesh named 'collision' is insufficient.

For dynamic/breakable objects, inspect a compatible base and current Fragment support. Do not invent physics flags or assume a static prop template has damage behavior.

## Archetype and resource

Resolve placement -> archetype -> asset and dictionaries. Inspect type/name, bounds, sphere, texture/physics dictionary links and unload behavior. Do not fill optional dictionaries with a guessed filename. Recalculate bounds after geometry changes.

For a map that places a custom static prop, this is a starting manifest:

~~~lua
fx_version 'cerulean'
game 'gta5'
this_is_a_map 'yes'
files { 'stream/example_props.ytyp' }
data_file 'DLC_ITYP_REQUEST' 'stream/example_props.ytyp'
~~~

Substitute the actual filename. Put game assets in stream/. The map marker is for map delivery; a spawn-only library needs its suitable manifest. Do not add a framework or spawn script without a task need.

Review the YMAP and generated _manifest.ymf dependencies for map delivery. Avoid copied lua54 declarations: current Cfx documentation marks that setting deprecated. This example is an integration pattern, not a live-tested resource.

## Sources

Checked 2026-10-15:
- [Sollumz Drawable conversion](https://docs.sollumz.org/tutorials/creating-props/converting-to-drawable): hierarchy and LOD assignment.
- [Sollumz archetype format](https://docs.sollumz.org/documentation/archetype-definition.ytyp): asset/dictionary relationships.
- [Cfx collision guide](https://docs.fivem.net/docs/assets-manual/beginner-series/part-5/).
- [Cfx resource manifest](https://docs.fivem.net/docs/scripting-reference/resource-manifest/).
- [Cfx data file types](https://docs.fivem.net/docs/game-references/data-files/): DLC_ITYP_REQUEST.
- [CodeWalker](https://github.com/dexyfex/CodeWalker): check installed-version support.

The separate Sollumz 'Creating the Archetype' tutorial was a placeholder when checked. Do not treat it as an implemented tutorial.
