# Web control panel ↔ Unreal (Remote Control API)

Remote Control API is **Beta**. MCP = for the agent to build the scene (editor only). Remote Control = for the user's/client's web panel (editor and packaged builds).

## Enable
- Edit > Plugins > Messaging > **Remote Control API** (restart). Optional: Remote Control Web Interface.
- HTTP server default **30010** (Project Settings > Web Remote Control). Console: `WebControl.StartServer`, `WebControl.StopServer`, `WebControl.EnableServerOnStartup 1`.
- WebSocket default **30020** (`ws://127.0.0.1:30020`).
- Bound to 127.0.0.1 by default. Other devices need `DefaultBindAddress` under `[HTTPServer.Listeners]` in `DefaultEngine.ini` — Epic warns: LAN/VPN only, never the public internet. Ask the user before changing it.
- Packaged build / `-game`: Remote Control is **off** — launch with `-RCWebControlEnable -RCWebInterfaceEnable`.

## HTTP routes used here
| Route | Purpose |
|---|---|
| `GET /remote/info` | lists routes; the probe uses it as "is anything listening" |
| `GET /remote/presets` | lists Remote Control Presets |
| `PUT /remote/object/describe` | `{"objectPath": "..."}` → properties and functions of an object |
| `PUT /remote/object/call` | call a function (see below) |
| `PUT /remote/object/property` | read/write a property (`access`: READ_ACCESS / WRITE_ACCESS / WRITE_TRANSACTION_ACCESS) |
| `PUT /remote/search/assets` | find assets (mesh/material paths for swaps) |
| `PUT /remote/batch` | several requests in one |
| `/remote/object/event` | experimental (`WebControl.EnableExperimentalRoutes 1`) |

### Call body
```json
{
  "objectPath": "/Game/Maps/House.House:PersistentLevel.Sofa_2",
  "functionName": "SetActorLocation",
  "parameters": { "NewLocation": { "X": 100, "Y": 0, "Z": 30 }, "bSweep": true },
  "generateTransaction": true
}
```
Other AActor functions (standard engine API):
- `SetActorRotation` — `{"NewRotation": {"Pitch":0,"Yaw":90,"Roll":0}, "bTeleportPhysics": false}`
- `SetActorScale3D` — `{"NewScale3D": {"X":1,"Y":1,"Z":1}}`
- `K2_SetActorLocation` is the Blueprint-exposed name of SetActorLocation in some versions — if the call fails with "function not found", `describe` the actor and use the name it lists (unverified which one 5.8 accepts).

`generateTransaction: true` makes the change undoable in the editor (Ctrl+Z). Ignored in packaged builds.

### Finding objectPath
In the editor: right-click the actor > Copy Reference, or `describe` a level path. Format: `/Game/<Map path>.<MapName>:PersistentLevel.<ActorName>`. Paths break when the actor is renamed or moved to a sublevel — another reason for a manager actor.

## Recommended design: FurnitureManager actor (experience value)
Place one Blueprint actor `BP_FurnitureManager` in the level with BlueprintCallable functions:
- `MoveSlot(Slot: Name, Location: Vector)`, `RotateSlot(Slot, Yaw: float)`, `ScaleSlot(Slot, Scale: float)`
- `SwapSlotMesh(Slot, Mesh: StaticMesh soft path)`
- `SetSlotMaterial(Slot, MaterialInstance: soft path, ElementIndex: int)`
- a `Map<Name, Actor>` of slots filled in the Details panel.

The panel then calls one stable objectPath. Expose the functions through a **Remote Control Preset** if you want Epic's web app or `preset.register` events. Blueprint graphs can't be authored from Python — build it by hand (5 minutes) or with an MCP that edits Blueprints (EngineWire).

Direct alternative without a manager: call `SetMaterial` on the actor's StaticMeshComponent (`.../Sofa_2.StaticMeshComponent0`, parameters `{"ElementIndex":0,"Material":"/Game/.../MI_Fabric_Green.MI_Fabric_Green"}`) — works, but paths are long and fragile.

## WebSocket form
```json
{"MessageName":"http","Parameters":{"Url":"/remote/object/call","Verb":"PUT","Body":{ ...same body... }}}
```
`preset.register` subscribes to preset events (PresetFieldsChanged) — useful to keep several panels in sync.

## Security (URemoteControlSettings)
- `bRestrictServerAccess` + `AllowedOrigin`: restrict which web origins may call. A page opened from `file://` sends `Origin: null`; serving it with `python -m http.server 8080 --bind 127.0.0.1` gives `http://127.0.0.1:8080` to allow-list (CORS behaviour untested).
- `bEnforcePassphraseForRemoteClients` + passphrases: required from non-localhost clients. Never put a passphrase in the HTML file you commit.
- Keep **off**: `bEnableRemotePythonExecution` (Epic flags possible vulnerabilities), remote console commands, any-remote-function calls.
- Default values for these settings: unverified — check Project Settings > Web Remote Control.
- Web app port 30000: unverified.

## The bundled panel (`assets/furniture-panel/index.html`)
- Edit the `CONFIG` block: `host`, `port`, `actors` (label + objectPath + start transform), `materialSwap` (objectPath, functionName, parameter builder) and the material list.
- `ALLOW_NON_LOCALHOST_TARGET = false` blocks any host other than 127.0.0.1/localhost/[::1]. Change it only after the user agrees and has set a passphrase + AllowedOrigin.
- Every request and response goes to the on-page log; "Dry run" shows the body without sending.
- The panel sends the passphrase in a `Passphrase` header when `CONFIG.passphrase` is set — the exact header name UE expects is unverified; check the log for 401/403 and the current docs.
- Tested only against a local stub server (request bodies for move/rotate/scale/material and the non-localhost refusal), not against a live Unreal Editor.

## Sources
- Overview: https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-for-unreal-engine
- Quick start: https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-quick-start-for-unreal-engine
- HTTP reference: https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-http-reference-for-unreal-engine
- WebSocket reference: https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-websocket-reference-for-unreal-engine
- Settings: https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/RemoteControlCommon/URemoteControlSettings
