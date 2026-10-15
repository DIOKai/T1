# Outdoor map acceptance

Choose exact coordinates/routes and log the resource set for repeatability.

| Check | Test | Pass criterion |
| --- | --- | --- |
| References | Fresh-open packaged data | Referenced assets are present or declared dependencies |
| Placement | Visit boundaries, road ties and entrances | No unintended overlap, floating geometry or terrain gaps |
| Collision | Walk/drive the route in both directions | No falls, invisible walls, wheel sinking or blocked intended paths |
| Streaming | Approach from several directions at walking/driving speed | No missing sections on the tested routes |
| LOD | Inspect near/mid/far views including replaced stock objects | No stale distant geometry, duplicate silhouettes or broken transitions |
| Occlusion | Orbit affected structures | No disappearance from valid viewpoints |
| Lights | Repeat key viewpoints by day/night | No orphan lights and expected emissives |
| Lifecycle | Cold join/restart the test resource | Consistent placement without duplicate scripted entities |
| Compatibility | Compare isolated/full resource sets | Conflicts identified by filename/resource and resolved in scope |
| Multiplayer | When required, repeat with two clients | Intended behavior agrees |

Viewer-only checks do not establish gameplay, navigation or multi-client success. Mark unrun checks explicitly.

Dry-run review cases:
- A hidden stock building retains collision: investigate ownership and remaining layers.
- A distant original tower still appears: inspect world LOD references and conflicts.
- An outdoor road is requested: do not automatically create MLO rooms/portals.
