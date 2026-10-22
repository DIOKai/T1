# Lumen, Nanite, Movie Render Graph, packaging, Pixel Streaming

## Lumen for interiors
Project Settings > Rendering:
- Dynamic Global Illumination Method = Lumen; Reflection Method = Lumen.
- Generate Mesh Distance Fields = on (needed for software ray tracing).
- Support Hardware Ray Tracing = on if the GPU is RTX 2000 / RX 6000 / Arc A or newer (higher quality, traces real triangles). Software Lumen runs on SM6 hardware from about a GTX 1070.
- Best mirrors/glossy floors: HWRT + Ray Lighting Mode = **Hit Lighting for Reflections** (project-wide or per Post Process Volume).

Post Process Volume (Infinite Extent on) knobs:
| Problem | Knob |
|---|---|
| small objects black in reflections, light leaking | Lumen Scene Detail ↑ |
| splotchy multi-bounce in glossy interiors | Lumen Scene Quality ↑ |
| leaks through walls | Max Trace Distance; thicker walls (≥10 cm) |
| GI lags after a light changes (web panel toggles lamps) | Final Gather Lighting Update Speed ↑ temporarily, put it back after |
| interior too dark/bright when moving between rooms | Exposure: Manual or a narrow min/max EV (experience value) |

Limits: tiny emissive meshes get culled (enable Emissive Light Source on lamp shades/strips); no Forward Shading; no VR; static lightmaps don't apply.

Daylight setup (experience value): Directional Light (sun) + Sky Light (real-time capture) + Sky Atmosphere + Exponential Height Fog; windows let the sun in, Rect Lights in window openings only if rooms stay too dark.

## Nanite
Opaque + Masked only. Glass/translucent: normal static mesh. Nanite meshes get full Lumen GI/reflections and Virtual Shadow Maps; ray tracing uses a Fallback Mesh (lower Fallback Relative Error for detail). Requires DX12 + SM 6.6 atomics.

## Movie Render Graph (MRG)
- Sequence: Level Sequence + Cine Camera Actor (focal length 18–35 mm for interiors, experience value), keyframed camera; plan shots with `archviz-cinematic`.
- Graph: Temporal Samples on the **Sampling Method** node (global); Spatial Samples on the **Renderer** node (per layer). Each layer chooses **Path Tracer** or **Deferred**.
  - Deferred = Lumen look, minutes for a whole clip; use for drafts and animation-heavy shots.
  - Path Tracer = reference quality, much slower indoors and with bright materials (one archviz user: ~7 min per HD frame). Use for stills or short hero shots.
- Always render a short low-sample test, time it, and give the user the projected total before the full run.
- MRG still lacks some MRQ features (nDisplay, High Resolution Rendering, ProRes, FCP XML) per the transition doc — check the version they run. Production-readiness in 5.8: unverified.
- Output EXR/PNG sequences, then encode with ffmpeg locally (free).

## Packaging a first-person walkthrough
General knowledge, not re-checked page by page for 5.8:
1. Add the First Person template content (or a simple Character with a camera), set it as the default pawn in a GameMode, set the map as Game Default Map.
2. Collision on walls/floors, box collision on furniture, blocking volumes at open edges.
3. Platforms > Windows > Package Project to a **new empty folder** (or `RunUAT BuildCookRun`). Long — ask first.
4. For the web panel: start the .exe with `-RCWebControlEnable -RCWebInterfaceEnable` (Remote Control is off in packaged builds and `-game`).

## Pixel Streaming (optional)
- Streams the running app to a browser/phone via WebRTC; keyboard/mouse/touch input and custom HTML UI.
- Plugin: Pixel Streaming or Pixel Streaming 2. Launch with `-PixelStreamingURL=ws://127.0.0.1:8888` (optionally `-RenderOffScreen`).
- Signalling server: `EpicGamesExt/PixelStreamingInfrastructure` (clone the `UE5.x` branch) or `get_ps_servers` under `Engine\Plugins\Media\PixelStreaming\Resources\WebServers` (downloads files — ask). Then `setup.bat` (admin PowerShell) and `start_with_stun.bat` in `SignallingWebServer\platform_scripts\cmd`; ports 80 + 8888; open `http://127.0.0.1`.
- Needs a GPU with hardware video encoding (details unverified). Local/LAN = free; public hosting = your own server or cloud GPU = **paid**, so don't propose it unless the user asks, and say it costs money.

## Sources
- Lumen technical details: https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine
- Nanite: https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- MRQ → MRG: https://dev.epicgames.com/documentation/unreal-engine/transitioning-to-the-movie-render-graph-from-movie-render-queue-in-unreal-engine
- Path Tracer: https://dev.epicgames.com/documentation/unreal-engine/path-tracer-in-unreal-engine
- Path tracing archviz report: https://cgarchitect.com/projects/4f54a56d-path-tracing-unreal-engine-5
- Pixel Streaming: https://dev.epicgames.com/documentation/en-us/unreal-engine/getting-started-with-pixel-streaming-in-unreal-engine , https://dev.epicgames.com/documentation/en-us/unreal-engine/pixel-streaming-in-unreal-engine
- Hardware specs: https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine
- Remote Control in packaged builds: https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-for-unreal-engine
