# Sources

## Videos studied (transcripts + frames, 2026-11-08)

- 8UKNKSnminQ — Melange 3D, "How to Model iPhone 17 Pro Max in Blender" (Blender 4.5.1): https://www.youtube.com/watch?v=8UKNKSnminQ
- Rg8kUXj842w — JOYCE 3D, "Blender Product Modeling Tutorial – Smartwatch Full Process Breakdown" (Blender 4.3.2, LoopTools + Bool Tool): https://www.youtube.com/watch?v=Rg8kUXj842w
- 6DQTDMM-6CQ — Bady Design, "Create a FiveM Prop from ONE Image!" (narration is music/ads; steps read from frames; its paid generator Meshy is replaced by free local Hunyuan3D): https://www.youtube.com/watch?v=6DQTDMM-6CQ

The notes are original summaries; no video content is redistributed.

## Documentation (checked 2026-11-08)

- Sollumz "Creating Static Meshes": Convert to Drawable, Sollumz LODs (active mesh = High), NORMAL shader, "Set all Materials Embedded", Export with ytyp, YMAP + _manifest.ymf. https://docs.sollumz.org/tutorials/creating-static-meshes
- Sollumz "Creating Static Collisions": apply Location, Create Bounds > Convert to Composite, empties at 0,0,0, prefer Bound Poly Box/Capsule/Sphere over mesh. https://docs.sollumz.org/tutorials/creating-static-collisions
- Sollumz collisions doc (missing Flag Preset is a common mistake): https://docs.sollumz.org/2.6/documentation/collisions.ybn
- Blender Bevel modifier manual: Percent width, Weight limit uses `bevel_weight_edge`, Miter Arc, Grid Fill, Clamp Overlap, Harden Normals (needs custom normals; created automatically). https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/bevel.html
- Weighted Normal modifier for hard surface (Gleb Alexandrov): https://www.blendernation.com/2020/02/13/weighted-normal-blender-2-8x-tutorial/ ; manual: https://docs.blender.org/manual/zh-hant/dev/modeling/modifiers/normals/weighted_normal.html
- Decimate vs retopo + bake for dense meshes: https://blenderartists.org/t/how-can-i-reduce-the-polygon-count-of-my-model-without-completely-ruining-the-detail/1446335 ; free BSurface retopo + normal bake guide (Intel): https://www.intel.com/content/dam/develop/external/us/en/documents/retopologizing-vr-and-game-assets-using-blender.pdf

Not verified: the Hunyuan3D 2.x built-in face-reduction option and its defaults (check the repo before relying on it); exact Sollumz shader names in the current release; whether Folders2YTD is still maintained (third-party download, so ask before installing).
