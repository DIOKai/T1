# Official pipeline references

Use live documentation as the source of truth when versions differ.

- Sollumz installation and supported Blender versions: https://docs.sollumz.org/getting-started/installation
- Sollumz basic clothing/ped editing: https://docs.sollumz.org/tutorials/basic-clothes-editing
- Drawable Dictionary (`.ydd`) structure: https://docs.sollumz.org/2.4/documentation/drawable-dictionary.ydd
- Sollumz feature support and known format limitations: https://docs.sollumz.org/features
- Cfx.re asset creation series: https://docs.fivem.net/docs/assets-manual/beginner-series/part-3/

Important verified points:

- Streamed freemode peds use separate component YDDs; a working body view commonly needs HEAD, UPPER, LOWR, and FEET components.
- Ped components need the appropriate external YFT skeleton during import so bone and vertex-group names resolve.
- Clothing/ped assets normally require high, medium, and low LOD attention.
- Normal/specular texture requirements, skin UV behavior, vertex colors, and shader details are component/material specific. Verify them against the current Sollumz documentation and a known-good base asset.
- Sollumz support changes by version. Never infer binary import/export support from an old tutorial; inspect the installed version and current feature page.

