# Layout JSON (`floorplan-to-blender/1`)

One file describes the building; scripts never guess anything that isn't in it. Plan coordinates: metres, X to the right, Y up the page (flip image Y when you measure from pixel rows), origin at a clear corner (e.g. the outside corner of the exterior wall at bottom-left). `assets/example-layout.json` is a complete small flat.

```json
{
  "schema": "floorplan-to-blender/1",
  "units": "m",
  "source": {
    "type": "plan_image | pdf | photos | listing_text | ai_ref",
    "files": ["plan.png"],
    "scale": {"method": "dimension_string | scale_bar | room_label | door_width | area | user_given",
              "px_per_m": 84.2,
              "samples": [{"label": "12'-6\"", "px": 320.5, "m": 3.81}],
              "error_pct": 1.2},
    "listing_area": {"value": 1450, "unit": "ft2 | m2", "standard": "ANSI Z765 | unknown"}
  },
  "levels": [{"id": "L1", "elevation": 0.0, "height": 2.74, "slab_thickness": 0.2}],
  "walls": [{
    "id": "W1", "level": "L1", "kind": "exterior | interior",
    "path": [[0, 0], [10.2, 0], [10.2, 8.4]], "closed": false,
    "thickness": 0.2, "thickness_source": "measured | default",
    "justify": "center | left | right",
    "height": null, "base_offset": 0.0, "free_ends": false
  }],
  "openings": [{
    "id": "D1", "wall": "W1", "segment": 0,
    "type": "door | sliding_door | garage_door | window | opening",
    "offset": 3.2, "offset_ref": "start | center",
    "width": 0.91, "height": 2.03, "sill": 0.0,
    "swing": "in_left | in_right | out_left | out_right | none"
  }],
  "rooms": [{
    "id": "R1", "name": "Living", "level": "L1",
    "polygon": [[0.1, 0.1], [5, 0.1], [5, 4], [0.1, 4]],
    "floor_finish": "wood | tile | carpet", "ceiling_height": null,
    "open_to": ["R2"],
    "label_area": {"value": 210, "unit": "ft2"}
  }],
  "stairs": [{
    "id": "S1", "from": "L1", "to": "L2", "type": "straight | L | U",
    "start": [6, 1], "direction": [0, 1], "width": 0.9,
    "risers": 15, "riser": 0.18, "tread": 0.28
  }],
  "notes": ["Hall closet depth guessed 0.6 m"]
}
```

## Field notes
- **walls.path** is the wall axis. `justify: center` puts half the thickness each side; `left` puts the whole wall on the left of the direction of travel, `right` on the right. For a closed exterior loop drawn counter-clockwise the left side is the inside, so `justify: left` keeps the path on the outside face (useful when the plan dimensions outside faces); clockwise loops need `right`. With `center`, the path is the wall centre line.
- **Corners** are mitered automatically between consecutive segments of the same wall. Where an interior wall meets another wall (T-junction), end its path on the other wall's face — not its axis — or the two walls overlap.
- **height** null = the level height. `base_offset` lifts a wall (e.g. a half wall on a step).
- **free_ends: true** silences the "end touches nothing" warning for intentionally free walls (kitchen peninsula, half wall).
- **openings.segment** counts from 0 along the path (for closed walls the last segment runs from the last point back to the first). `offset` is metres along that segment from its start point to the opening's start (`offset_ref: start`) or centre (`center`).
- **sill** is height above the level floor; doors use 0.
- **rooms.polygon** is the floor area inside the walls (wall faces), used for floors, ceilings, area checks and the door-reachability check. Keep it 1–2 cm inside the faces.
- **rooms.open_to** lists rooms this one opens into with no wall between (open-plan living/kitchen, a hall that is part of the living room). The reachability check uses it; without it, open-plan rooms are reported as having no door.
- **stairs**: only `straight` is built by the script; the others are kept for Bonsai or manual modelling. `risers × riser` should equal the next level's elevation, and the script builds `risers − 1` treads (the last riser lands on the upper floor), so the run length is `(risers − 1) × tread`; Blender won't cut the upper slab — do it by hand or with `bonsai-stairs`.
- Anything you guessed goes in `notes` or a `*_source` field so the report can list it.
