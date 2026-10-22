# Shot plan: start on a small thing, pull out to the place

The pattern in the viral temple video: every shot opens tight on a detail (moss on a lantern cap, a gold pillar cap, a bracket set, a petal on raked gravel) and the camera moves back until the building and its setting fill the frame. In film terms this is a pull-back / dolly-out reveal: the camera physically moves away, so perspective changes as the world opens up (a zoom-out from one spot looks flatter). Slow pull-backs read as calm and often close a scene; fast ones are a reveal of scale. (Glossary-level sources, vendor wording — treat as vocabulary, not rules.) Procedural scenes suit this because the detail is generated to the same scale as the whole, so there is no switch between a "hero asset" and the environment.

## Plan before animating
List ~10 shots in a table and agree it with the user. Put each in the plan's `shots` array so `check_site_plan.py` checks that the target exists, the camera really ends farther away than it starts, and the straight path doesn't pass through a building.

| # | start on (element) | first frame | end frame includes | lens mm (start→end) | s | move | light |
|---|---|---|---|---|---|---|---|
| 1 | pond_lantern | moss on the cap, water behind | lantern, bridge, pagoda | 85→35 | 8 | back + up 6 m | morning |
| 2 | pagoda bracket set (1st roof) | bracket arms and blocks | whole pagoda + hall roof | 70→28 | 10 | back + rise | morning |
| 3 | gold cap on a hall pillar | metal against vermilion | hall front + podium steps | 85→35 | 8 | back along the axis | noon |
| 4 | petal on raked gravel | gravel ridges | garden + rocks + hall veranda | 100→35 | 9 | crane up | noon |
| 5 | bridge railing finial | lacquer detail | full arch + its reflection | 70→28 | 8 | back + side | afternoon |
| 6 | lantern window on the approach | paper / light | lantern pair + gate | 85→35 | 7 | back down the path | dusk |
| 7 | gate roof tile end | tile pattern | gate framing the pagoda | 85→35 | 8 | back + down to eye level 1.6 m | dusk |
| 8 | cherry blossom cluster | blossoms, shallow focus | tree + pond edge | 100→50 | 8 | back | dusk |
| 9 | pagoda finial rings | the nine rings | pagoda against sky | 135→50 | 10 | back + down | blue hour |
| 10 | (close) lantern flame | flame | whole complex from above | 85→24 | 12 | long back + up, end on a 2 s hold | night |

Numbers are starting points (unverified), in the same spirit as `archviz-cinematic`'s shot table.

## Rules for each shot
- **First frame**: the detail must be modelled for that distance — if the bracket set is a box, the shot fails. Tell the owning zone agent which details will be seen up close (add it to its brief).
- **Move**: 2–4 keys, ease in and out, roll 0, speed that reads as calm (start slow, the move can accelerate a little as the frame widens). Prefer a real dolly/crane path; a zoom-only change is a different, flatter look.
- **Path**: nothing between start and end that the camera would pass through (checked for buildings; check trees by eye). For a long pull-back past a tree or gate, route it with a curve, not a straight line.
- **Focus**: rack focus from the detail to the far subject, or deep focus at the end.
- **End frame**: hold ~1–2 s, verticals straight (keep the camera level and use lens shift in Blender; in three.js keep `camera.up` and avoid tilting for architecture).
- **Continuity**: same time-of-day order as the list; shots cut on motion.

## Where to build it
- Blender stills/film: `archviz-cinematic` (camera helper, flicker-free Cycles sequence, ffmpeg).
- three.js real-time: `threejs-camera-controls-and-rigs` (spline rigs) and `threejs-animation`; record with the browser or render frames via `threejs-image-pipeline`.
