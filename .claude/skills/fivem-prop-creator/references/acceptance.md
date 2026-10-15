# Prop acceptance

Log game build, model name, coordinates, tool versions and resource set.

| Check | Test | Pass criterion |
| --- | --- | --- |
| Identity | Fresh-open exported output | Mesh/textures resolve without an unlisted source folder |
| Scale/pivot | Place next to a known-size object and rotate | Dimensions and origin match the brief |
| Collision | Walk around/onto/under it and test intended vehicle contact | No unintended pass-through, blockage, snagging or falling |
| Appearance | Inspect close-up and both sides in daylight/night/rain | No missing textures, wrong normals or unintended alpha artifacts |
| LOD | Approach/retreat from multiple directions | Intended silhouette and transitions match the project criteria |
| Lifecycle | Cold join and restart the isolated resource | Result loads consistently |
| Dynamics | If requested, push, impact, damage or break | Required behavior matches the agreed base and brief |
| Conflicts | Start with neighboring target resources | No unrelated replacements or name collisions |

Record actual observations/screenshots or 'not run'. A successful export cannot substitute for collision or gameplay tests.

Dry-run review cases:
- Convert an existing large-YTD prop 1:1: preserve binaries and report size.
- Make a vase shatter: verify a breakable path, not just a static YDR.
- Deliver from a Blender screenshot: distinguish viewer/game checks that remain untested.
